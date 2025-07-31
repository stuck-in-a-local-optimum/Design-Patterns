package LLD.designpatterns.abstractfactory;


import LLD.designpatterns.abstractfactory.concretefactories.TataFactory;
import LLD.designpatterns.abstractfactory.products.Bike;
import LLD.designpatterns.abstractfactory.products.Car;

public class main {
    public static void main(String[] args) {
        VehicleFactory factory = new TataFactory();
        Car car = factory.createCar();
        Bike bike = factory.createBike();
        car.drive();
        bike.ride();


    }
}
