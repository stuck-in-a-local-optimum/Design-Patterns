package LLD.designpatterns.observer;

public class Main {

    public static void main(String[] args) {

        //Demonstrate the Observer Design Pattern
        System.out.println("==============================Observer Design Pattern========================================================");
        Subject iphone16ProOberservable = new Iphone16Pro();
        EmailAlertObserver emailAlertObserver1 = new EmailAlertObserver("emailObserver1@gmail.com");
        EmailAlertObserver emailAlertObserver2 = new EmailAlertObserver("emailObserver2@gmail.com");
        SmsAlertObserver smsAlertObserver1 = new SmsAlertObserver("9876543210");
        iphone16ProOberservable.addObserver(emailAlertObserver1);
        iphone16ProOberservable.addObserver(emailAlertObserver2);
        iphone16ProOberservable.addObserver(smsAlertObserver1);
        iphone16ProOberservable.updateStock(10);
        iphone16ProOberservable.updateStock(0);
        iphone16ProOberservable.updateStock(10);


    }
}
