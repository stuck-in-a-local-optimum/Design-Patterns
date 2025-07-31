package LLD.designpatterns.abstractfactory;

import LLD.designpatterns.abstractfactory.products.Bike;
import LLD.designpatterns.abstractfactory.products.Car;

public interface VehicleFactory {
    Car createCar();
    Bike createBike();
}
