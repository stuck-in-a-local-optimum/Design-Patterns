package LLD.designpatterns.abstractfactory.concretefactories;

import LLD.designpatterns.abstractfactory.VehicleFactory;
import LLD.designpatterns.abstractfactory.concreteproducts.BMWBike;
import LLD.designpatterns.abstractfactory.concreteproducts.BMWCar;
import LLD.designpatterns.abstractfactory.products.Bike;
import LLD.designpatterns.abstractfactory.products.Car;

public class BMWFactory implements VehicleFactory {
    @Override
    public Car createCar() {
        return new BMWCar();
    }

    @Override
    public Bike createBike() {
        return new BMWBike();
    }
}
