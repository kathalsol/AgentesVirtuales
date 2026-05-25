# Diseño del Protocolo de Evaluación y Matriz de Consistencia

## Definición de Condiciones (Apartado A)

### Condición Experimental (Condición A)

El agente virtual a evaluar es una representación de un adulto mayor con características técnicas, visuales y conductuales específicas. Visualmente, presenta un aspecto humano estilizado y semi-realista con un diseño limpio y amigable que facilita la interacción con el usuario. En términos conductuales, el agente exhibe movimientos suaves y naturales durante la animación, lo que contribuye a una experiencia más intuitiva y acogedor. Técnicamente, el modelo está equipado con dos tipos de blendshapes que permiten expresiones faciales básicas, aunque esta configuración presenta limitaciones para implementar un lip sync avanzado.

### Condición de Control o Baseline (Condición B)

La condición de control corresponde a una interfaz conversacional basada en interacción por voz, sin la presencia de un componente visual o agente animado. El usuario se comunica con el sistema mediante reconocimiento y síntesis de voz, escuchando respuestas de audio en tiempo real, pero sin visualizar ningún avatar o representación gráfica del agente. Esta condición permite evaluar el impacto específico de la dimensión visual y la animación del agente en la experiencia del usuario, aislando la interacción a través del canal de voz solamente. De este modo, se puede determinar cómo la presencia de un agente animado afecta la percepción, confianza y satisfacción del usuario en comparación con una experiencia puramente auditiva.

### Justificación

Esta comparación entre la Condición A y la Condición B permite aislar y medir el impacto real de las características visuales y conductuales del agente virtual. El diseño experimental mantiene constantes todas las variables excepto la presencia del componente visual animado, garantizando que cualquier diferencia en los resultados sea atribuible exclusivamente a la representación visual del agente. Ambas condiciones comparten el mismo sistema conversacional, las mismas respuestas de voz y contenido de interacción; la única variable independiente que cambia es la presencia del agente visual animado, lo que asegura que los resultados no se confundan con otros factores como la calidad del contenido, la síntesis de voz o la plataforma de interacción. Esta comparación permite medir específicamente cómo la presencia de un agente visual adulto mayor afecta la percepción de confianza y credibilidad del sistema, el nivel de satisfacción y engagement del usuario, la comodidad emocional durante la interacción, la efectividad comunicativa percibida, y la disposición del usuario a continuar interactuando. Al eliminar la variable visual en la Condición B, se puede cuantificar el aporte diferencial que tiene la representación visual animada en la experiencia global del usuario, proporcionando evidencia sobre la relevancia del agente virtual en contextos de interacción conversacional.

## Matriz de Consistencia Metodológica (Apartado B)

| Pregunta de Investigación (RQ) | Variable o Constructo | Instrumento Validado | Tarea Asociada |
|---|---|---|---|
| RQ1: ¿En qué medida el uso de un agente virtual de compañía reduce los niveles de soledad en adultos mayores? | Percepción de soledad / Impacto emocional y social | UCLA Loneliness Scale | El participante realiza una serie de interacciones conversacionales con el agente (en la Condición A con avatar 3D o en la Condición B solo por voz) sobre temas de interés personal, compartiendo experiencias y sentimientos. Se aplica el cuestionario antes y después de la sesión de interacción. |
| RQ2: ¿Cómo fue percibido el agente virtual como herramienta de acompañamiento en adultos mayores? | Percepción del agente / Usabilidad, aprendizaje y satisfacción | Agent Rating Questionnaire (ARQ) | El participante interactúa con el agente a través de múltiples turnos de conversación, incluyendo tareas de consulta de información, expresión de preocupaciones y solicitud de orientación. Se evalúa cómo el agente fue percibido en términos de credibilidad, utilidad y capacidad de acompañamiento. |
| RQ3: ¿Cuál es la percepción de la experiencia de usuario sobre el agente virtual como herramienta de acompañamiento? | Experiencia de usuario / Facilidad de uso, satisfacción general y usabilidad | User Experience Questionnaire (UEQ) | El participante completa una sesión completa de interacción que incluye: iniciación del sistema, navegación por opciones de conversación, mantener un diálogo natural y finalizar la sesión. Se evalúa la calidad general de la experiencia incluyendo aspectos de atracción, eficiencia y dependencia. |

## Adaptación del Protocolo del Investigador (Apartado C - HTML)

Ver el documento [Protocolo.html](Protocolo.html) para la guía detallada de procedimientos del investigador, que incluye instrucciones paso a paso para la conducción de la sesión experimental, administración de consentimiento informado, asignación de grupos, recolección de datos, y protocolos de cierre.

## Justificación Teórica en HCI (Apartado D)

### Embodiment y Comunicación No Verbal según Justine Cassell

El diseño del agente virtual como una representación humana estilizada y semi-realista se fundamenta en la teoría del embodiment de Justine Cassell [1][2], quien propone que los agentes virtuales con cuerpos y rostros tienen mayor capacidad para establecer comunicación significativa con los usuarios. Cassell enfatiza que la presencia de un avatar 3D facilita la transmisión de información no verbal a través de gestos, expresiones faciales y movimientos corporales, elementos que enriquecen la calidad de la interacción conversacional. En nuestro diseño, los movimientos suaves y naturales del agente, combinados con las expresiones faciales permitidas por los blendshapes, implementan esta capacidad comunicativa no verbal. Aunque nuestro modelo tiene limitaciones técnicas (solo dos tipos de blendshapes), estos mecanismos de embodiment son suficientes para criar un sentido de presencia social y facilitar la percepción de autenticidad en la interacción, especialmente importante en contextos de acompañamiento emocional con adultos mayores.

### Soporte Relacional y Lazos Afectivos según Timothy Bickmore

La elección de representar al agente como un adulto mayor se alinea con la investigación de Timothy Bickmore [3] sobre el diseño de agentes relacionales y la construcción de lazos afectivos duraderos. Bickmore argumenta que los usuarios establecen vínculos emocionales más fuertes cuando el agente exhibe características demográficas similares o complementarias a las suyas, y que la consistencia en la personalidad y el comportamiento del agente refuerza la confianza y el compromiso en la relación humano-computadora. El aspecto visual del agente adulto mayor crea un contexto de identificación y reciprocidad generacional que puede facilitar la apertura emocional del usuario adulto mayor. Adicionalmente, los movimientos suaves y la expresión facial amigable del agente transmiten calidez y capacidad de escucha activa, elementos clave en el modelo de agentes relacionales que Bickmore propone como esenciales para mantener interacciones significativas a largo plazo.

### Efecto Proteus y Variaciones de Comportamiento según Yee y Bailenson

La comparación experimental entre la Condición A (agente con avatar 3D) y la Condición B (solo voz) permite investigar el Efecto Proteus descrito por Nick Yee y Jeremy Bailenson [5]. Este efecto propone que la presencia de un avatar visual influye en el comportamiento del usuario de manera análoga a como lo haría un prototipo o una exposición visual. En el contexto de nuestro estudio, el Efecto Proteus sugiere que la visualización de un avatar adulto mayor amigable puede inducir cambios en cómo el usuario se comporta en la interacción, potencialmente aumentando su disposición a compartir información personal, su nivel de confianza en el sistema, y su percepción de credibilidad del agente. Se espera que usuarios en la Condición A (con avatar) exhiban mayores niveles de engagement emocional, mayor disposición a continuar la interacción y una percepción más positiva del acompañamiento en comparación con la Condición B. Este efecto es particularmente relevante en el estudio de agentes de compañía para adultos mayores, donde la presencia visual puede amplificar la sensación de interacción social auténtica y reducir la percepción de soledad de manera más efectiva que la interacción puramente auditiva.

## Referencias

[1] J. Cassell, H. H. Vilhjalmsson, and T. Bickmore, "BEAT: the Behavior Expression Animation Toolkit", in Proceedings of the 28th Annual Conference on Computer Graphics and Interactive Techniques, Los Angeles, CA, USA, 2001, pp. 477-486.

[2] J. Cassell, "Embodied conversational interface agents", Communications of the ACM, vol. 43, no. 4, pp. 70-78, 2000.

[3] T. Bickmore and R. W. Picard, "Establishing and maintaining long-term human-computer relationships", ACM Transactions on Computer-Human Interaction, vol. 12, no. 2, pp. 293-327, 2005.

[5] N. Yee and J. Bailenson, "The Proteus Effect: The effect of transformed self-representation on behavior", Human Communication Research, vol. 33, no. 3, pp. 271-290, 2007.