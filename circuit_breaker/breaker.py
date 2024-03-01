from datetime import datetime, timezone
from enum import Enum
import functools
import logging




class StateChoices(Enum):
    OPEN = "open"
    CLOSED = "closed"
    HALF_OPEN = "half_open"
    
    
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

class RemoteCallFailedException(Exception):
    pass


class CircuitBreaker:
    def __init__(self, func, exceptions, threshold, delay):
        """
        :param func: метод, который выполняет удаленный вызов
        :param exceptions: исключение или набор исключений для перехвата (в идеале это должны быть сетевые исключения)
        :param threshold: количество неудачных попыток до изменения состояния на "Открыто"
        :param delay: задержка в секундах между состоянием "Закрыто" и "Полуоткрыто"
        """
        self.func = func
        self.exceptions_to_catch = exceptions
        self.threshold = threshold
        self.delay = delay

        # by default set the state to closed
        self.state = StateChoices.CLOSED


        self.last_attempt_timestamp = None
        # keep track of failed attemp count
        self._failed_attempt_count = 0

    def update_last_attempt_timestamp(self):
        self.last_attempt_timestamp = datetime.now(timezone.utc).timestamp()

    def set_state(self, state):
        """To track the state changes by logging the information"""
        prev_state = self.state
        self.state = state
        logging.info(f"Changed state from {prev_state} to {self.state}")

    def handle_closed_state(self, *args, **kwargs):
        '''
        handle_closed_state делает удаленный вызов, если он успешный, то мы обновляем и возвращаем результат удаленного вызова.
        Если удаленный вызов завершается сбоем, то увеличивается. Если не достиг порогового значения,
        то просто вызовите исключение. Если больше или равно пороговому значению, мы изменяем состояние на Open и,
        наконец, возникает исключение.last_attempt_timestamp_failed_attempt_count_failed_attempt_count_failed_attempt_count
        '''
        
        allowed_exceptions = self.exceptions_to_catch
        try:
            ret_val = self.func(*args, **kwargs)
            logging.info("Success: Remote call")
            self.update_last_attempt_timestamp()
            return ret_val
        except allowed_exceptions as e:
            # remote call has failed
            logging.info("Failure: Remote call")
            # increment the failed attempt count
            self._failed_attempt_count += 1

            # update last_attempt_timestamp
            self.update_last_attempt_timestamp()

            # if the failed attempt count is more than the threshold
            # then change the state to OPEN
            if self._failed_attempt_count >= self.threshold:
                self.set_state(StateChoices.OPEN)
            # re-raise the exception
            raise RemoteCallFailedException from e

    def handle_open_state(self, *args, **kwargs):
        '''
        handle_open_state First проверяет, прошло ли несколько секунд с момента последней попытки совершить удаленный вызов.
        Если нет, то возникает исключение. Если с момента последней попытки прошло несколько секунд, то мы меняем состояние "Полуоткрыто".
        Теперь попробуем сделать один удаленный вызов к неисправному сервису. Если удаленный вызов прошел успешно, то меняем состояние на «Закрыто»
        и сбрасываем на 0 и возвращаем ответ удаленного вызова.
        Если удаленный вызов не удался, когда он находился в состоянии "Полуоткрыто",
        то состояние снова устанавливается в "Открыто" и мы вызываем исключение. delaydelay_failed_attempt_count
        '''
        current_timestamp = datetime.now(timezone.utc).timestamp()
        # if `delay` seconds have not elapsed since the last attempt, raise an exception
        if self.last_attempt_timestamp + self.delay >= current_timestamp:
            raise RemoteCallFailedException(f"Retry after {self.last_attempt_timestamp+self.delay-current_timestamp} secs")

        # after `delay` seconds have elapsed since the last attempt, try making the remote call
        # update the state to half open state
        self.set_state(StateChoices.HALF_OPEN)
        allowed_exceptions = self.exceptions_to_catch
        try:
            ret_val = self.func(*args, **kwargs)
            # the remote call was successful
            # now reset the state to Closed
            self.set_state(StateChoices.CLOSED)
            # reset the failed attempt counter
            self._failed_attempt_count = 0
            # update the last_attempt_timestamp
            self.update_last_attempt_timestamp()
            # return the remote call's response
            return ret_val
        except allowed_exceptions as e:
            # the remote call failed again
            # increment the failed attempt count
            self._failed_attempt_count += 1

            # update last_attempt_timestamp
            self.update_last_attempt_timestamp()

            # set the state to "OPEN"
            self.set_state(StateChoices.OPEN)

            # raise the error
            raise RemoteCallFailedException from e

    def make_remote_call(self, *args, **kwargs):
        if self.state == StateChoices.CLOSED:
            return self.handle_closed_state(*args, **kwargs)
        if self.state == StateChoices.OPEN:
            return self.handle_open_state(*args, **kwargs)
        
        
class APICircuitBreaker:
    def __init__(self, exceptions=(Exception,), threshold=5, delay=60):
        self.obj = functools.partial(
            CircuitBreaker,
            exceptions=exceptions,
            threshold=threshold,
            delay=delay
        )

    def __call__(self, func):
        self.obj = self.obj(func=func)

        def decorator(*args, **kwargs):
            ret_val = self.obj.make_remote_call(*args, **kwargs)
            return ret_val

        return decorator

    def __getattr__(self, item):
        return getattr(self.obj, item)


circuit_breaker = APICircuitBreaker