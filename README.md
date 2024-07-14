# AccessKit Python bindings

These are the bindings to use AccessKit from Python.

Documentation for the Rust packages can be found [here](https://docs.rs/accesskit/latest/accesskit/).

An example program showing how to integrate AccessKit in a pygame application is available [here](https://github.com/AccessKit/accesskit-python/tree/main/examples/pygame).

## Building from a Source Distribution

If there are no wheels available for your platform, you will have to build one yourself. You will need to have Rust installed on your system, so that the native libraries can be compiled. Please visit [rustup.rs](https://rustup.rs) for instructions on how to proceed.

## Building from within the repository

This project uses [maturin](https://github.com/PyO3/maturin) as its build tool. If you need to manually build wheels for development purposes, it is recommended to install it inside a virtual environment. All maturin commands must be issued from this repository's root directory.

## Contributing

Contributions to AccessKit are welcome. Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

AccessKit is licensed under the [Apache License, Version 2.0](LICENSE-APACHE) or the [MIT license](LICENSE-MIT), at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in AccessKit by you, as defined in the Apache License, shall be dual-licensed as above, without any additional terms or conditions.

The list of authors for copyright purposes is in the [AUTHORS](AUTHORS) file.

Significant portions of AccessKit are derived from Chromium and are covered by its [BSD-style license](LICENSE.chromium).
