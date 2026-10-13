from abc import ABC , abstractmethod

class StatsObserver(ABC):
   
    @abstractmethod
    def update(self , url_id: int, date_time: str , referer : str , client_ip : str):
        pass
    
