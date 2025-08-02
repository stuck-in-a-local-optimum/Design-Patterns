package LLD.designpatterns.observer;

public interface Subject {

    void addObserver(NotificationAlertObserver observer);
    void removeObserver(NotificationAlertObserver observer);
    void notifyObservers();

    void updateStock(int stock);
}
