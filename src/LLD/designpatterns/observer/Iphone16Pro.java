package LLD.designpatterns.observer;

import java.util.ArrayList;
import java.util.List;

public class Iphone16Pro implements Subject {
    private String name;
    List<NotificationAlertObserver> observers = new ArrayList<>();
    int currentStock = 0; //initially 0
    @Override
    public void addObserver(NotificationAlertObserver observer) {
        this.observers.add(observer);

    }

    @Override
    public void removeObserver(NotificationAlertObserver observer) {
        this.observers.remove(observer);

    }

    @Override
    public void notifyObservers() {
        for(NotificationAlertObserver observer : observers){
            observer.update();
        }

    }

    @Override
    public void updateStock(int stock) {
        if(currentStock == 0){
            notifyObservers();
        }
        currentStock = stock;

    }
}
