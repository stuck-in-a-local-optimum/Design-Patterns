package LLD.designpatterns.abstractfactory.concreteproducts;

import LLD.designpatterns.abstractfactory.products.Bike;

public class TataBike implements Bike {
    @Override
    public void ride() {
        System.out.println("Riding TataBike");
    }
}
