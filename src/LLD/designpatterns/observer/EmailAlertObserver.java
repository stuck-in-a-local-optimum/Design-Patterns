package LLD.designpatterns.observer;

public class EmailAlertObserver implements NotificationAlertObserver {
    private String emailId;
    private Iphone16Pro iphone16Pro;

    public EmailAlertObserver(String emailId){
        this.emailId = emailId;
    }
    @Override
    public void update() {
        sendEmail(emailId, "Hurry up, product is back in stock!!");

    }

    private void sendEmail(String emailId, String message){
        System.out.println(message);
        System.out.println("mail sent to id: " + emailId);
        System.out.println("---------------------------------------------");

    }
}
