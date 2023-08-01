use pyo3::prelude::*;
use pyo3::types:PyAny;
use pyo3::wrap_pyfunction;

use std::threads;

#[pyclass]
struct MyThreads {}

#[pymenthods]
impl MyThreads {
    #[args(func)]
    fn run(&self, py: Python, func: &PyAny) -> PyResult<PyObject>{
        let callable = func.to_object(py);
        let handle = thread::spawn(move || {
            let gil = Python::acquire_gil();
            let py = gil.python();
            let result = callable.call0(py).unwrap();
            result.to_object(py);
        });
        let output = handle.join().unwrap();
        Ok(output)
    }
}

#[pymodule]
fn my_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MyThreads>()?;
    Ok(())
}


