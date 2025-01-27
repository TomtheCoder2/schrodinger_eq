mod complex;

use std::f64::consts::PI;
use std::ops::Mul;
use complex::Complex;

const L: f64 = 10.0; // Spatial domain size
const N: usize = 500; // Number of spatial points
const T: f64 = 2.0; // Simulation time
const DELTA_X: f64 = 2.0 * L / N as f64; // Spatial step size
const DELTA_T: f64 = 0.001; // Time step size
const HBAR: f64 = 1.0; // Reduced Planck constant (scaled)
const MASS: f64 = 1.0; // Particle mass (scaled)

fn initialize_wavefunction() -> Vec<Complex<f64>> {
    let mut wavefunction = Vec::new();
    for i in 0..N {
        let x = -L + i as f64 * DELTA_X;
        let gaussian = (-x.powi(2) / 2.0).exp(); // Gaussian wave packet
        wavefunction.push(Complex::new(gaussian, 0.0));
    }
    wavefunction
}

fn potential(x: f64) -> f64 {
    if x > -0.5 && x < -0.4 || x > 0.4 && x < 0.5 {
        0.0 // Slits
    } else if x > -1.0 && x < 1.0 {
        1e6 // Barrier
    } else {
        0.0 // Free space
    }
}

impl std::ops::Mul<Complex<f64>> for f64 {
    type Output = Complex<f64>;

    fn mul(self, rhs: Complex<f64>) -> Self::Output {
        Complex {
            re: self * rhs.re,
            im: self * rhs.im,
        }
    }
}

fn evolve_wavefunction(wavefunction: &mut Vec<Complex<f64>>, potential: &Vec<f64>) {
    let mut new_wavefunction = wavefunction.clone();
    for i in 1..N - 1 {
        let laplacian = wavefunction[i + 1] - 2.0 * wavefunction[i] + wavefunction[i - 1];
        let kinetic = -HBAR / (2.0 * MASS * DELTA_X.powi(2)) * laplacian;
        let potential_energy = potential[i] * wavefunction[i];
        new_wavefunction[i] += Complex::i() * DELTA_T * (kinetic + potential_energy);
    }
    *wavefunction = new_wavefunction;
}

use eframe::egui;
use egui_plot::{Plot, PlotPoints};

fn main() -> Result<(), eframe::Error> {
    eframe::run_native(
        "Double-Slit Experiment Simulation",
        eframe::NativeOptions::default(),
        Box::new(|_| Ok(Box::new(SimulationApp::default()))),
    )
}

struct SimulationApp {
    wavefunction: Vec<Complex<f64>>,
    potential: Vec<f64>,
}

impl Default for SimulationApp {
    fn default() -> Self {
        let wavefunction = initialize_wavefunction();
        let potential: Vec<f64> = (0..=N)
            .map(|i| -L + i as f64 * DELTA_X)
            .map(|x| potential(x))
            .collect();
        Self {
            wavefunction,
            potential,
        }
    }
}

impl eframe::App for SimulationApp {
    fn update(&mut self, ctx: &egui::Context, _: &mut eframe::Frame) {
        // Evolve the wavefunction
        evolve_wavefunction(&mut self.wavefunction, &self.potential);

        // Render the wavefunction probability density
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Double-Slit Experiment");
            ui.label("Wavefunction Probability Density");
            for (i, psi) in self.wavefunction.iter().enumerate() {
                let x = -L + i as f64 * DELTA_X;
                // ui.add(
                    // let sin: PlotPoints = (0..1000).map(|i| {
                    //     let x = i as f64 * 0.01;
                    //     [x, x.sin()]
                    // }).collect();
                    // let line = Line::new(sin);
                    // Plot::new("my_plot").view_aspect(2.0).show(ui, |plot_ui| plot_ui.line(line));
                    Plot::new("Probability").show(ui, |plot| {
                        let points: PlotPoints = self
                            .wavefunction
                            .iter()
                            .enumerate()
                            .map(|(i, psi)| {
                                let x = -L + i as f64 * DELTA_X;
                                [x, psi.norm_sqr().powi(2)]
                            })
                            .collect();
                        let line = egui_plot::Line::new(points);
                        plot.line(line);
                    });
                // );
            }
        });
    }
}
