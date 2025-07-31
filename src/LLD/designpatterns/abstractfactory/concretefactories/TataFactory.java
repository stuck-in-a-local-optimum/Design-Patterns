package LLD.designpatterns.abstractfactory.concretefactories;

import LLD.designpatterns.abstractfactory.VehicleFactory;
import LLD.designpatterns.abstractfactory.concreteproducts.TataBike;
import LLD.designpatterns.abstractfactory.concreteproducts.TataCar;
import LLD.designpatterns.abstractfactory.products.Bike;
import LLD.designpatterns.abstractfactory.products.Car;

public class TataFactory implements VehicleFactory {
    @Override
    public Car createCar() {
        return new TataCar();
    }

    @Override
    public Bike createBike() {
        return new TataBike();
    }
}
