from observers.interface import StatsObserver

class ObserverSubject:

    def __init__(self ):
        self.observers: list[StatsObserver] = []
        
    def add(self , observer : StatsObserver) -> None:
        if observer not in self.observers: 
            self.observers.append(observer)
    
    def remove(self , observer : StatsObserver) -> None:
        self.observers.remove(observer)
    
    def notify_observers(self , url_id , date_time , referer , client_ip) -> None:
        for observer in self.observers:
            observer.update(url_id ,  date_time , referer , client_ip)

stats_obs = ObserverSubject()