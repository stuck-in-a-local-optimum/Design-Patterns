package LLD.designpatterns.abstractfactory.concreteproducts;

import LLD.designpatterns.abstractfactory.products.Bike;

public class BMWBike implements Bike {
    @Override
    public void ride() {
        System.out.println("Riding BMW bike");
    }
}
