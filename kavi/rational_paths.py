"""Exact rational execution through acquired integer circuits.

Sign handling, fraction normalization and division semantics are engineered.
The compatible program search may acquire compositions of these operations.
"""

from dataclasses import dataclass,replace
from fractions import Fraction
import json

from .procedure_core import ProcedureLibrary,Limits,ExecutionLimit,expression,node_count


@dataclass(frozen=True)
class ScalarProcedure:
    name: str
    arity: int
    body: tuple | None = None


@dataclass
class ScalarExecution:
    value: Fraction = Fraction(0)
    calls: int = 0
    gates: int = 0
    iterations: int = 0
    frames: int = 0


class RationalLibrary:
    def __init__(self,backend):
        self.backend=backend
        if set(backend.procedures)!={'add','subtract','multiply'}:
            raise ValueError('Require exactly addition, subtraction and multiplication dependencies')
        self.procedures={name:ScalarProcedure(name,2) for name in ('add','subtract','multiply','divide')}

    @staticmethod
    def scalar(value):
        if type(value) not in (int,Fraction):
            raise ValueError('Use exact integers or fractions; floating point is not admitted')
        value=Fraction(value)
        if max(abs(value.numerator).bit_length(),value.denominator.bit_length())>4096:
            raise ValueError('Scalar exceeds the declared 4096-bit component bound')
        return value

    def validate(self,expr,arity,depth=0):
        if depth>12 or not isinstance(expr,tuple) or len(expr)<2:
            raise ValueError('Invalid scalar expression')
        if expr[0]=='arg':
            if len(expr)!=2 or type(expr[1]) is not int or not 0<=expr[1]<arity:
                raise ValueError('Invalid scalar argument')
        elif expr[0]=='const':
            if len(expr)!=2 or type(expr[1]) is not int or expr[1] not in (0,1):
                raise ValueError('Only zero and one are supplied constants')
        elif expr[0]=='call' and expr[1] in self.procedures:
            if len(expr)!=2+self.procedures[expr[1]].arity:
                raise ValueError('Scalar call arity mismatch')
            for child in expr[2:]: self.validate(child,arity,depth+1)
        else:
            raise ValueError('Scalar iteration or unknown operation is unsupported')

    def add(self,name,arity,body):
        if (name in self.procedures or not name.isidentifier() or len(name)>40
                or not 1<=arity<=3 or len(self.procedures)>=32):
            raise ValueError('Invalid scalar procedure')
        self.validate(body,arity)
        if node_count(body)>32: raise ValueError('Scalar procedure exceeds node limit')
        self.procedures[name]=ScalarProcedure(name,arity,body)

    def execute_expr(self,expr,args,*,limits=Limits(),check=lambda:None):
        self.validate(expr,len(args))
        args=tuple(self.scalar(x) for x in args)
        result=ScalarExecution()
        try: result.value=self._eval(expr,args,result,limits,check,0)
        except Exception as error:
            error.execution=result
            raise
        return result

    def apply(self,tag,name,values,*,limits=Limits(),check=lambda:None):
        if tag!='call': raise ValueError('Scalar loop semantics are not supplied')
        return self.execute_expr(('call',name,*(('arg',i) for i in range(len(values)))),values,limits=limits,check=check)

    def _eval(self,expr,args,out,limits,check,depth):
        check()
        if depth>limits.max_depth: raise ExecutionLimit('Scalar depth budget exhausted')
        if expr[0]=='arg': return args[expr[1]]
        if expr[0]=='const': return Fraction(expr[1])
        values=tuple(self._eval(c,args,out,limits,check,depth+1) for c in expr[2:])
        if out.calls>=limits.max_calls: raise ExecutionLimit('Scalar call budget exhausted')
        out.calls+=1
        proc=self.procedures[expr[1]]
        if proc.body is not None: return self._eval(proc.body,values,out,limits,check,depth+1)
        a,b=values

        def integer(name,x,y):
            remaining=replace(limits,max_calls=limits.max_calls-out.calls,
                              max_gates=limits.max_gates-out.gates,max_iterations=limits.max_iterations-out.iterations)
            try: observed=self.backend.execute(name,(x,y),limits=remaining,check=check)
            except Exception as error:
                partial=getattr(error,'execution',None)
                if partial:
                    for key in ('calls','gates','iterations','frames'): setattr(out,key,getattr(out,key)+getattr(partial,key))
                raise
            for key in ('calls','gates','iterations','frames'): setattr(out,key,getattr(out,key)+getattr(observed,key))
            return observed.value

        def signed_multiply(x,y):
            value=integer('multiply',abs(x),abs(y))
            return -value if (x<0)!=(y<0) else value

        def signed_add(x,y):
            if (x<0)==(y<0):
                value=integer('add',abs(x),abs(y))
                return -value if x<0 else value
            large,small=sorted((abs(x),abs(y)),reverse=True)
            value=integer('subtract',large,small)
            return -value if (x if abs(x)>=abs(y) else y)<0 else value

        if proc.name in ('add','subtract'):
            left=signed_multiply(a.numerator,b.denominator)
            right=signed_multiply(b.numerator,a.denominator)
            numerator=signed_add(left,-right if proc.name=='subtract' else right)
            denominator=integer('multiply',a.denominator,b.denominator)
        elif proc.name=='multiply':
            numerator=signed_multiply(a.numerator,b.numerator)
            denominator=integer('multiply',a.denominator,b.denominator)
        else:
            if b==0: raise ValueError('Division by zero is undefined')
            numerator=signed_multiply(a.numerator,b.denominator)
            if b.numerator<0: numerator=-numerator
            denominator=integer('multiply',a.denominator,abs(b.numerator))
        # Canonical gcd normalization is supplied host arithmetic, not learned gates.
        return self.scalar(Fraction(numerator,denominator))

    def to_dict(self):
        return {'schema':'kavi.rational-library.v1','backend':self.backend.to_dict(),
                'engineered_semantics':'signed fractions; canonical gcd normalization; division with nonzero denominator',
                'procedures':[{'name':p.name,'arity':p.arity,'body':p.body} for p in self.procedures.values() if p.body is not None]}

    def encoded(self):
        return (json.dumps(self.to_dict(),sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')

    @classmethod
    def from_dict(cls,value):
        if value['schema']!='kavi.rational-library.v1': raise ValueError('Unknown scalar library schema')
        library=cls(ProcedureLibrary.from_dict(value['backend']))
        for entry in value['procedures']: library.add(entry['name'],entry['arity'],expression(entry['body']))
        return library
