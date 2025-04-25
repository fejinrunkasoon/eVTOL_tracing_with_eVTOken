import pickle
import uuid

PICKLE_SEPARATOR =uuid.uuid4().hex
obj1={"name":"Alice","age":30}
obj2=[1,2,3,4]
obj3="Hello,World!"

serialized_data = (
    pickle.dumps(obj1)+PICKLE_SEPARATOR.encode()+
    pickle.dumps(obj2)+PICKLE_SEPARATOR.encode()+
    pickle.dumps(obj3)
)
print(serialized_data)

parts =serialized_data.split(PICKLE_SEPARATOR.encode())
deserialized_objects =[pickle.loads(part)for part in parts]
print(deserialized_objects)
