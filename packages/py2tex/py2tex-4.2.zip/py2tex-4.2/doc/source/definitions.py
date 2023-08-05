# definitions.py
#
# \PythonDefIntern{%}{\mathbin{\PythonKeyword{mod}}}
# \PythonDef{a_vec}{\vec{a}}
# \PythonLet{a_1}\PythonSubscriptV
# \PythonLet{a_2}\PythonSubscriptV
# \PythonLet{print_i}\PythonSubscript
# \PythonDefIntern{print}{\underbar{\PythonKeyword{\smash{print}}}}
if a_vec == [a_1, a_2]:
    print print_i (a_vec)

# Somewhat more intricate customization.
#
# \PythonDefaultIntern{print}
# \def\BuiltIn##1##2##3{%
#   {\if ##1F \underline{\smash{##2{##3}}}%
#    \else \hbox{\sc ##3}%
#    \fi}}
# \PythonLet{repr}\BuiltIn
# \PythonLet{str}\BuiltIn
print repr (repr), str (str), foo (bar)
