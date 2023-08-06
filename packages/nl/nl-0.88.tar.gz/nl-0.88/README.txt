= nl

nl is a python library that provides a production system with an API modelled on the natural language.

More info can be found in http://bitbucket.org/enriquepablo/nl/wiki/Home.

To install, see INSTALL.txt in this same directory.


intro: theory

Un sistema declarativo, en el que se introducen frases y reglas de producción, y del que se extraen respuestas.

La idea es acercarse a la sintaxis y poder expresivo del ln.

Hay diversos sistemas con un objetivo parecido o relacionado. Intentaré introducir nl a través de un pequeño repaso a estos sistemas precedentes.

Lógica de primer orden.
La lógica de primer orden (LPO) es el primer antecedente de nl que vamos a considerar. La LPO es la culminación de un largo proceso filosófico y matemático, previo al desarrollo las primeras computadoras, y tiene una serie de característics que no la hacen apropiada para ser usada mecánicamente por las mismas.
Estática: no aplicable a procesos en tiempo real. -> monotónica.
Tendencia al infinito. A considerar universos infinitos, en conjuntos infinitos de símbolos y axiomas.
Excesivamente prolija si se usan sus reglas de producción de una manera mecánica.
Interpretada en universos matemáticos inmutables.
Pensada para analizar a mano estos universos, eternos, para asegurar teoremas manualmente.

Lógicas no monotónicas.
Con la aparición de las computadoras, se tiende a eliminar verbosidad y a mantener conjuntos de verdades que son función del tiempo real.
Cláusulas de horn -> parsimonia.

hay dos avenidas básicas iniciales:

Forward chaining, o sistemas productivos. Un ejemplo es CLIPS. Con estos sistemas se pueden modelar únicamente universos finitos, ya que una vez extendidos, contienen todas las verdades posibles en su dominio de interpretación. Por ejemplo, la aritmética de peano no se puede exresar en estos sistemas, pues la definición de sucesión generaría una productividad ilimitada.

Backward chaining. El ejemplo más ilustre es prolog. Con estos sistemas se pueden modelar universos infinitos. El problema con ellos es la necesidad de símbolos extralógicos (en prolog, el cut) para evitar recursiones infinitas. Por ejemplo, no se puede expresar la transitividad de la relación de subconjunto en una teoría conjuntista sin recurrir al cut:

subset(S1, S3) :- subset(S1, S2) , subset(S2, S3).

Estos sistemas se han usado para producir teorías especializadas, con un campo semántico estrecho, máquinas de estado capaces de simular procesos.
Interpretadas en dominios cerrados, en procesos específicos.

El último (a lo mejor penúltimo) tipo de sistemas que han aparecido son los DL.
Son básicamente teorías conjuntistas, distintas axiomatizaciones de un patrón basico común centrado en las reloaciones de pertenencia y subconjunto. El descbrimiento es que embebiendo esas relaciones básicas en la implementación del sistema se puede conseguir un sistema mucho más expresivo y potente. Se reduce mucho la prolijidad.

Estos sistemas, de nuevo, se usan para producir teorías interpretadas en dominios especializados. 

Sobre las DL se ha creado la web semántica.
Se trata de producir un sistema lógico en red que sea capaz de hablar y razonar sobre los recursos disponibles en esa red.
La interpretación de esta web semántica es algo más complicada. De lo dicho anteriormente se sigue que su dominio de interpretación son los recursos de la red. Pero los recursos de la web son a su vez representaciones de objetos externos (o no) a la web. ¿De qué objetos? De los objetos que forman el universo de discurso del lenguaje natural. Aquellos objetos de los que hablamos son los que representamos en la web. De modo que aquí se podría hablar de un "tetraisomorfismo", si es que existe esa palabra. Tenemos la web semántica, que habla de los recursos de la web, que a su vez representan a objetos extráneos, de los cuales habla el lenguaje natural. La web semántica se quiere para que hable de los reursos de la red de la misma forma en que nosotros hablamos de los objetos que éstos representan. Pero claro, el lenguaje natural no es realmente un isomorfismo de la realidad de que habla, quizá se podría decir todavía; no conocemos la verdad de manera absoluta, la ciencia no ha llegado a un punto en el que se haya dicho: se acabó, ya está terminada, ya lo sabemos todo. De modo que en principio, la web semántica hablaría imperfectamente de lo representado. ¿A dónde quiero llegar con todo ésto? Pues a que se podría considerar que el dominiode interpretación de la web semántica es el propio lenguaje natural. 

Y la idea sería cojer los predicados conjuntistas e interpretarlos en el uso natural del verbo copulativo. Es decir, "juan pertenece a la clase de los hombres" se interpreta en "juan es un hombre", y "hombre es un subconjunto de animal" se interpreta en "un hombre es un animal". A partir de aquí, se añaden nuevos verbos y nombres comunes como predicados y clases en la teoría, con lo que podemos hablar de cualquier cosa; y además, se igualan clases con predicados, al prescribir que para cada podsible predicación, le corresponde una clase anónima.

Curiosamente ése fue el origen de los verbos conjuntistas: un intento de formalizar el uso del lenguaje natural. Durante años, Frege y Russell tuvieron esa idea mientras desarrollaban la LPO.

Paradoja de Russell.

OWL-DL, OWL-Full. Se divorcia la correspondencia con las construcciones del ln de la posibilidad de razonamiento. En OWL-Full es posible expresar la paradoja de Russell.

Salida propuesta por nl. El objetivo es 

predicados sólo los conjuntistas. Los demás verbos se asimilan a operaciones. los hechos perteneces a hecho.

Una lógica muy simple, pero que nos permite decir todo lo necesario.
