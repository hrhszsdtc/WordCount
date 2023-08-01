use pyo3::prelude::*;
use pyo3::types::PyAny;

use std::mem;
use std::thread;

#[pyclass]
struct MyThreads {}

#[pymethods]
impl MyThreads {
    #[args(func)]
    fn run(&self, py: Python, func: &PyAny) -> PyResult<()> {
        if !func.is_callable() {
            return Err(pyo3::exceptions::PyTypeError::new_err(
                "func is not callable",
            ));
        }
        let callable = func.to_object(py);
        let handle = thread::spawn(move || {
            let gil = Python::acquire_gil();
            let py = gil.python();
            match callable.call0(py) {
                Ok(result) => result.into_py(py),
                Err(e) => e.into_py(py),
            }
        });
        mem::forget(handle);
        Ok(())
    }
}

#[pymodule]
#[pyo3(name = "my_threads")]
fn my_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MyThreads>()?;
    Ok(())
}
