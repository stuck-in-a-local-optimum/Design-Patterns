package LLD.designpatterns.observer;

public class SmsAlertObserver implements NotificationAlertObserver {
    private String phoneNumber;
    private Iphone16Pro iphone16Pro;

    public SmsAlertObserver(String  phoneNumber){
        this.phoneNumber = phoneNumber;
    }
    @Override
    public void update() {
        sendSms(phoneNumber, "Hurry up, product is back in stock!!");

    }

    private void sendSms(String phoneNumber, String messsage) {
        System.out.println(messsage);
        System.out.println("Sms sent to mobile no: "+ phoneNumber);
        System.out.println("---------------------------------------------");

    }
}
