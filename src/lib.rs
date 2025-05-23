// Copyright 2023 The AccessKit Authors. All rights reserved.
// Licensed under the Apache License, Version 2.0 (found in
// the LICENSE-APACHE file) or the MIT license (found in
// the LICENSE-MIT file), at your option.

// TODO: Remove this exception once we update pyo3.
#![allow(non_local_definitions)]

mod common;
mod geometry;

#[cfg(target_os = "macos")]
mod macos;
#[cfg(any(
    target_os = "linux",
    target_os = "dragonfly",
    target_os = "freebsd",
    target_os = "netbsd",
    target_os = "openbsd",
))]
mod unix;
#[cfg(target_os = "windows")]
mod windows;

use pyo3::{prelude::*, types::PyCapsule};
use std::ffi::c_void;

pub use common::*;
pub use geometry::*;

#[pymodule]
fn accesskit(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<::accesskit::Role>()?;
    m.add_class::<::accesskit::Action>()?;
    m.add_class::<::accesskit::Orientation>()?;
    m.add_class::<::accesskit::TextDirection>()?;
    m.add_class::<::accesskit::Invalid>()?;
    m.add_class::<::accesskit::Toggled>()?;
    m.add_class::<::accesskit::SortDirection>()?;
    m.add_class::<::accesskit::AriaCurrent>()?;
    m.add_class::<::accesskit::Live>()?;
    m.add_class::<::accesskit::HasPopup>()?;
    m.add_class::<::accesskit::ListStyle>()?;
    m.add_class::<::accesskit::TextAlign>()?;
    m.add_class::<::accesskit::VerticalOffset>()?;
    m.add_class::<::accesskit::TextDecoration>()?;
    m.add_class::<Node>()?;
    m.add_class::<Tree>()?;
    m.add_class::<TreeUpdate>()?;
    m.add_class::<ActionDataKind>()?;
    m.add_class::<ActionRequest>()?;
    m.add_class::<Affine>()?;
    m.add_class::<Point>()?;
    m.add_class::<Rect>()?;
    m.add_class::<Size>()?;
    m.add_class::<Vec2>()?;

    #[cfg(target_os = "macos")]
    {
        let macos_module = PyModule::new(py, "macos")?;
        macos_module.add_class::<macos::QueuedEvents>()?;
        macos_module.add_class::<macos::Adapter>()?;
        macos_module.add_class::<macos::SubclassingAdapter>()?;
        macos_module.add_function(wrap_pyfunction!(
            macos::add_focus_forwarder_to_window_class,
            macos_module
        )?)?;
        m.add_submodule(macos_module)?;
    }
    #[cfg(any(
        target_os = "linux",
        target_os = "dragonfly",
        target_os = "freebsd",
        target_os = "netbsd",
        target_os = "openbsd",
    ))]
    {
        let unix_module = PyModule::new(py, "unix")?;
        unix_module.add_class::<unix::Adapter>()?;
        m.add_submodule(unix_module)?;
    }
    #[cfg(target_os = "windows")]
    {
        let windows_module = PyModule::new(py, "windows")?;
        windows_module.add_class::<windows::QueuedEvents>()?;
        windows_module.add_class::<windows::Adapter>()?;
        windows_module.add_class::<windows::SubclassingAdapter>()?;
        m.add_submodule(windows_module)?;
    }

    Ok(())
}

// The following exception is needed because this function is only used
// in the bindings for some platform adapters.
#[allow(dead_code)]
fn to_void_ptr(value: &PyAny) -> *mut c_void {
    if let Ok(value) = value.extract::<&PyCapsule>() {
        return value.pointer();
    }
    let value = value.getattr("value").unwrap_or(value);
    value.extract::<isize>().unwrap() as *mut _
}
