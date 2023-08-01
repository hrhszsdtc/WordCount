use pyo3::prelude::*;
use pyo3::types::PyAny;
use pyo3::wrap_pyfunction;

use std::thread;

#[pyclass]
struct MyThreads {}

#[pymethods]
impl MyThreads {
    #[args(func)]
    fn run(&self, py: Python, func: &PyAny) -> PyResult{
        let callable = func.to_object(py);
        let handle = thread::spawn(move || {
            let gil = Python::acquire_gil();
            let py = gil.python();
            let result = callable.call0(py).unwrap();
            result.into_py(py);
        });
        let output = handle.join().unwrap();
        Ok(output.into())
    }
}

#[pymodule(my_threads)]
fn my_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MyThreads>()?;
    Ok(())
}


