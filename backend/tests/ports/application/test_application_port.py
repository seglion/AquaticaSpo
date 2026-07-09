import pytest
import inspect
from app.ports.application.services import PortService






def test_portservice_exists():
    # Solo verificamos que la clase existe y es tipo ABC
    assert PortService is not None
    
def test_create_port_method_exists():
    # Verificamos que PortService tiene el método create_port
    assert hasattr(PortService, "create_port")
    method = getattr(PortService, "create_port")
    assert callable(method)

def test_create_port_method_signature():
    method = getattr(PortService, "create_port", None)  # OJO: desde la clase, no desde instancia
    assert method is not None and callable(method)

    sig = inspect.signature(method)
    params = list(sig.parameters.values())

    expected_params = ['self', 'name', 'country', 'latitude', 'longitude']
    actual_params = [param.name for param in params]

    assert actual_params == expected_params, f"Expected parameters {expected_params} but got {actual_params}"
    
def test_create_port_is_abstract_method():
    # Obtenemos el método de la clase
    method = getattr(PortService, "create_port", None)
    assert method is not None

    # Verificamos que el método tiene el atributo __isabstractmethod__ y es True
    assert getattr(method, "__isabstractmethod__", False) is True
 
 
 
 
 
 
 
 
    
def test_get_port_by_id_method_exists():
# Verificamos que PortService tiene el método create_port
    assert hasattr(PortService, "get_port_by_id")
    method = getattr(PortService, "get_port_by_id")
    assert callable(method)
    
    
def test_get_port_by_id_method_signature():
    method = getattr(PortService, "get_port_by_id", None)  # OJO: desde la clase, no desde instancia
    assert method is not None and callable(method)

    sig = inspect.signature(method)
    params = list(sig.parameters.values())

    expected_params = ['self', 'port_id']
    actual_params = [param.name for param in params]

    assert actual_params == expected_params, f"Expected parameters {expected_params} but got {actual_params}"
    
def test_get_port_by_id_abstract_method():
    # Obtenemos el método de la clase
    method = getattr(PortService, "get_port_by_id", None)
    assert method is not None

    # Verificamos que el método tiene el atributo __isabstractmethod__ y es True
    assert getattr(method, "__isabstractmethod__", False) is True
    
    
    
    

def test_list_ports_method_exists():
# Verificamos que PortService tiene el método create_port
    assert hasattr(PortService, "list_ports")
    method = getattr(PortService, "list_ports")
    assert callable(method)

def test_list_ports_abstract_method():
    # Obtenemos el método de la clase
    method = getattr(PortService, "list_ports", None)
    assert method is not None

    # Verificamos que el método tiene el atributo __isabstractmethod__ y es True
    assert getattr(method, "__isabstractmethod__", False) is True
    
    
    
    
    
def test_update_port_method_exists():
# Verificamos que PortService tiene el método create_port
    assert hasattr(PortService, "update_port")
    method = getattr(PortService, "update_port")
    assert callable(method)

def test_update_port_abstract_method():
    # Obtenemos el método de la clase
    method = getattr(PortService, "update_port", None)
    assert method is not None

    # Verificamos que el método tiene el atributo __isabstractmethod__ y es True
    assert getattr(method, "__isabstractmethod__", False) is True

def test_update_port_method_signature():
    method = getattr(PortService, "update_port", None)  # OJO: desde la clase, no desde instancia
    assert method is not None and callable(method)

    sig = inspect.signature(method)
    params = list(sig.parameters.values())

    expected_params = ['self', 'port_id']
    actual_params = [param.name for param in params]

    assert actual_params == expected_params, f"Expected parameters {expected_params} but got {actual_params}"    

def test_delete_port_method_exists():
# Verificamos que PortService tiene el método create_port
    assert hasattr(PortService, "delete_port")
    method = getattr(PortService, "delete_port")
    assert callable(method)

def test_delete_port_abstract_method():
    # Obtenemos el método de la clase
    method = getattr(PortService, "delete_port", None)
    assert method is not None

    # Verificamos que el método tiene el atributo __isabstractmethod__ y es True
    assert getattr(method, "__isabstractmethod__", False) is True
    
def test_delete_port_method_signature():
    method = getattr(PortService, "delete_port", None)  # OJO: desde la clase, no desde instancia
    assert method is not None and callable(method)

    sig = inspect.signature(method)
    params = list(sig.parameters.values())

    expected_params = ['self', 'port_id']
    actual_params = [param.name for param in params]

    assert actual_params == expected_params, f"Expected parameters {expected_params} but got {actual_params}"    