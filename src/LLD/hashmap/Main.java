package LLD.hashmap;

import java.util.Random;

public class Main {

        public static void main(String[] args) {
            MyHashMap<Integer, String> myHashMap = new MyHashMap<>(15);

            Random random = new Random();
            for (int i = 0; i < 17; i++) {
                int key = i;  // random key between 0-99
                String value = "Value" + random.nextInt(1000);  // random string like Value875
                myHashMap.put(key, value);
                System.out.println("Inserted: Key = " + key + ", Value = " + value);
            }

            System.out.println("-------------------------------------------");
            System.out.println("Get key: " + myHashMap.get(2));
        }


}
