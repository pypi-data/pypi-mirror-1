import salamoia.h2o.tpg
from salamoia.h2o.search import *

def des(s):
    return s[1:-1]

class SearchParser(salamoia.h2o.tpg.Parser):
    r"""
    set lexer = ContextSensitiveLexer

    separator spaces: '\s+' ;

    token operator: '=' ; 
    token and: 'and' ;
    token or: 'or' ;
    token str: '("[^\"]*"|\'[^\']*\')' des;
    token partial: '([a-zA-Z0-9][a-zA-Z0-9\.@]*)?\*' ;
    token key: '[a-zA-Z0-9][a-zA-Z0-9\.@]*' ;
    token dn: '[a-zA-Z][a-zA-Z0-9\*\.@=,]*' ;

    START/e -> $e=AnySpec()$ (Expr/e|'\*')? $b=None$ $s=None$ (('->' | '@') (str/b | dn/b) )? (';' scope/s)? 
               $e=BaseSpec(e,s,b)$;

    Expr/s -> Term/s $a=[s]$ ( or Term/x $a.append(x)$ )+ $s=OrSpec(a)$ | Term/s ;
    Term/s -> Fact/s $a=[s]$ ( and Fact/x $a.append(x)$ )+ $s=AndSpec(a)$ | Fact/s ;
    Fact/s -> 'max' '\(' string/v '\)' $s=MaxSpec(v)$ |
              'owner' ('=' string/v $s=OwnerSpec(v)$ | 'in' '\(' Expr/v '\)' $s=SubOwnerSpec(v)$ ) |
              'type' '=' string/v $s=TypeSpec(v)$ |
              key/k 'in' '\[' string/x $a=[PropSpec(k,x)]$ ( ',' string/x $a.append(PropSpec(k,x))$ )+ $s=OrSpec(a)$ '\]' |
              key/k operator/op string/v $s=PropSpec(k, v, op)$ | 
              '\(' Expr/s '\)' ;

    string/s -> str/s | partial/s | key/s ;

    scope/x -> "base"/x | "sub"/x | "one"/x ;

    """


