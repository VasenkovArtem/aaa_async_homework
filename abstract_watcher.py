import abc
import asyncio
from typing import Coroutine, Any

"""
Описание задачи:
    Необходимо реализовать планировщик, позволяющий запускать и отслеживать фоновые корутины.
    Планировщик должен обеспечивать:
        - возможность планирования новой задачи
        - отслеживание состояния завершенных задач (сохранение результатов их выполнения)
        - отмену незавершенных задач перед остановкой работы планировщика
        
    Ниже представлен интерфейс, которому должна соответствовать ваша реализация.
    
    Обратите внимание, что перед завершением работы планировщика, все запущенные им корутины должны быть
    корректным образом завершены.
    
    В папке tests вы найдете тесты, с помощью которых мы будем проверять работоспособность вашей реализации
    
"""


class AbstractRegistrator(abc.ABC):
    """
    Сохраняет результаты работы завершенных задач.
    В тестах мы передадим в ваш Watcher нашу реализацию Registrator и проверим корректность сохранения результатов.
    """

    @abc.abstractmethod
    def register_value(self, value: Any) -> None:
        # Store values returned from done task
        ...

    @abc.abstractmethod
    def register_error(self, error: BaseException) -> None:
        # Store exceptions returned from done task
        ...


class AbstractWatcher(abc.ABC):
    """
    Абстрактный интерфейс, которому должна соответствовать ваша реализация Watcher.
    При тестировании мы рассчитываем на то, что этот интерфейс будет соблюден.
    """

    def __init__(self, registrator: AbstractRegistrator):
        self.registrator = registrator  # we expect to find registrator here

    @abc.abstractmethod
    async def start(self) -> None:
        # Good idea is to implement here all necessary for start watcher :)
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        # Method will be called on the end of the Watcher's work
        ...

    @abc.abstractmethod
    def start_and_watch(self, coro: Coroutine) -> None:
        # Start new task and put to watching
        ...


class StudentWatcher(AbstractWatcher):
    def __init__(self, registrator: AbstractRegistrator):
        super().__init__(registrator)
        # Your code goes here
        self.registrator = registrator
        self.tasks = []  # храним список созданных задач

    async def start(self) -> None:
        # Your code goes here
        # при новом запуске, если не было завершения,
        # завершаем все предыдущие задачи
        # и удаляем их из списка
        for task in self.tasks:
            task.cancel()
            # удаляем задачу из списка
            self.delete_from_tasks(task)

    def delete_from_tasks(self, task):
        try:
            self.tasks.remove(task)
        except ValueError:
            pass

    async def stop(self) -> None:
        # Your code goes here
        # ждём завершения задач, дадим им на это 100 секунд
        done, pending = await asyncio.wait(self.tasks, timeout=100)
        # for (done, pending) in self.tasks:
        # фиксируем результаты выполнения задач
        print(self.tasks)
        for task in done:
            print(task)
            # если без ошибок - то сохраняем результат выполнения
            try:
                self.registrator.register_value(task.result())
            # если получаем ошибку - сохраняем её
            except Exception as error:
                self.registrator.register_error(error)
            # удаляем задачу из списка
            self.delete_from_tasks(task)
        # отменяем незавершённые задачи
        for task in pending:
            task.cancel()
            # удаляем задачу из списка
            self.delete_from_tasks(task)

    def start_and_watch(self, coro: Coroutine) -> None:
        # Your code goes here
        # создаём новую задачу и сохраняем её в списке
        new_task = asyncio.create_task(coro)
        self.tasks.append(new_task)
