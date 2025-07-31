package hashmap;

public class MyHashMap<K, V> {
    private static int INITIAL_CAPACITY = 1 << 4; //fancy way to write 1*2^4 = 16
    private static int MAXIMUM_CAPACITY = 1 << 30; //as 2^31 is negative for signed-integer so next highest value with power of two is 2^30

    private Node<K, V>[] table;

    public MyHashMap(){
        this.table = new Node[INITIAL_CAPACITY];
    }

    public MyHashMap(int capacity){
        int tableSize = tableSizeFor(capacity);
        this.table = new Node[tableSize];
    }

    private int tableSizeFor(int cap) {
        int n = cap - 1;
        n |= n >>> 1;
        n |= n >>> 2;
        n |= n >>> 4;
        n |= n >>> 8;
        n |= n >>> 16;
        return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
    }

    public void put(K key, V value){
        int capacity = this.table.length;
        int index = (capacity - 1) & key.hashCode();

        Node<K, V> node = this.table[index];

        if(node == null){
            this.table[index] = new Node(key, value);
        } else {
            //collision
            Node<K, V> previousNode = node;
            while(node != null){
                if(node.getKey().equals(key)){
                    node.setValue(value);
                    this.table[index] = node;
                    return;
                }
                previousNode = node;
                node = node.getNextNode();
            }
            Node<K, V> newNode = new Node(key, value);
            previousNode.setNextNode(newNode);

        }
    }

    public V get(K key){
        int capacity = this.table.length;
        int index = (capacity - 1) & key.hashCode();

        Node node = this.table[index];

        while(node != null){
            if(node.getKey().equals(key)){
                return (V) node.getValue();
            }
            node = node.getNextNode();
        }
        return null;
    }




}
