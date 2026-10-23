# Verificação: classes novas exigidas pelo exercício?

Gerado em 2026-10-23 17:35 por `src/verificacao/verificar_classes_exigidas.py`.

## 1. O que os testes exigem além do esqueleto (todos os 129 exercícios)

| exercício | exigido pelos testes e ausente do esqueleto |
|---|---|
| go-counting | BLACK (outro), NONE (outro), WHITE (outro) |
| dot-dsl | ATTR (outro), EDGE (outro), NODE (outro) |

## 2. Classes novas nas soluções aceitas

| fonte | exercício | rótulo | classe nova | herda de | exigida pelos testes | exceção | nome citado no enunciado |
|---|---|---|---|---|---|---|---|
| referencia | bowling | oo | Frame | – | não | não | sim |
| referencia | ledger | oo | LCInfo | – | não | não | não |
| referencia | react | oo | Cell | – | não | não | não |
| referencia | rectangles | oo | Corners | – | não | não | não |
| referencia | robot-simulator | oo | Compass | – | não | não | não |
| referencia | simple-linked-list | oo | LinkedIterator | – | não | não | não |

## 3. Trechos do enunciado que falam de classes ou iteradores (para leitura manual)

**referencia / bowling**

> Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.
**referencia / simple-linked-list**

> ## Classes in Python
> The "canonical" implementation of a linked list in Python usually requires one or more `classes`.
> For a good introduction to `classes`, see the [concept:python/classes]() and companion exercise [exercise:python/ellens-alien-game](), or [Class section of the Official Python Tutorial][classes tutorial].
> ## Building an Iterator
> See [implementing an iterator for a class][custom iterators] for implementation details.
> Custom exceptions can be created through new exception classes (see [`classes`][classes tutorial] for more detail) that are typically subclasses of [`Exception`][exception base class].
> For situations where you know the error source will be a derivative of a certain exception _type_, you can choose to inherit from one of the [`built in error types`][built-in errors] under the _Exception_ class.
> To customize a generic _exception_, create a `class` that inherits from `Exception`.
> class EmptyListException(Exception):
> [built-in errors]: https://docs.python.org/3/library/exceptions.html#base-classes
> [classes tutorial]: https://docs.python.org/3/tutorial/classes.html#tut-classes
> [custom iterators]: https://docs.python.org/3/tutorial/classes.html#iterators
> [exception base class]: https://docs.python.org/3/library/exceptions.html#Exception
