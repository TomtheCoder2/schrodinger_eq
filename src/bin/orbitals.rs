use eframe::egui;
use plotly::common::ColorScale;
use plotly::{Plot, Surface};
use std::f64::consts::{E, PI};

#[derive(Clone, Copy, Debug)]
pub(crate) struct Complex<T> {
    pub(crate) re: T,
    pub(crate) im: T,
}

impl<T> Complex<T> {
    pub(crate) fn new(re: T, im: T) -> Self {
        Self { re, im }
    }
}

impl Complex<f64> {
    pub(crate) fn norm_sqr(&self) -> f64 {
        self.re * self.re + self.im * self.im
    }
}

impl std::ops::Add for Complex<f64> {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        Self {
            re: self.re + other.re,
            im: self.im + other.im,
        }
    }
}

impl std::ops::Mul<f64> for Complex<f64> {
    type Output = Self;

    fn mul(self, scalar: f64) -> Self {
        Self {
            re: self.re * scalar,
            im: self.im * scalar,
        }
    }
}

fn radial_wavefunction(n: u32, l: u32, r: f64) -> f64 {
    let rho = 2.0 * r / n as f64;
    let normalization = ((2.0 / n as f64).powi(3)
        * (factorial(n - l - 1) / (2 * n * factorial(n + l))) as f64)
        .sqrt();
    normalization * (rho.powi(l as i32) * (-rho / 2.0).exp())
}

fn spherical_harmonic(l: u32, m: i32, theta: f64, phi: f64) -> Complex<f64> {
    let normalization = ((2.0 * l as f64 + 1.0) / (4.0 * PI) * factorial(l - m.abs() as u32) as f64
        / factorial(l + m.abs() as u32) as f64) as f64;
    let assoc_legendre = (theta.cos().powi(m.abs())); // Simplified
    let phase = Complex::new((m as f64 * phi).cos(), (m as f64 * phi).sin());

    phase * normalization * assoc_legendre
}

fn factorial(n: u32) -> u32 {
    (1..=n).product()
}

struct OrbitalApp {
    n: u32,
    l: u32,
    m: i32,
    plot: Option<Plot>,
}

impl Default for OrbitalApp {
    fn default() -> Self {
        Self {
            n: 1,
            l: 0,
            m: 0,
            plot: None,
        }
    }
}

impl eframe::App for OrbitalApp {
    fn update(&mut self, ctx: &egui::Context, _: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.label("n:");
                ui.add(egui::DragValue::new(&mut self.n).clamp_range(1..=10));

                ui.label("l:");
                ui.add(egui::DragValue::new(&mut self.l).clamp_range(0..=self.n - 1));

                ui.label("m:");
                ui.add(
                    egui::DragValue::new(&mut self.m).clamp_range(-(self.l as i32)..=self.l as i32),
                );
            });

            if ui.button("Generate Plot").clicked() {
                self.plot = Some(generate_plot(self.n, self.l, self.m));
            }

            if let Some(plot) = &self.plot {
                ui.vertical(|ui| {
                    ui.label("3D Orbital Plot:");
                    let html = format!(r#"<html><header><script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script></header><body>{}</body>"#, plot.to_inline_html(Some("orbital-plot")));
                    
                    // ui.label(egui::RichText::new(html).monospace());
                    //save to file
                    let path = "orbital-plot.html";
                    std::fs::write(path, html).unwrap();
                });
            }
        });
    }
}

fn generate_plot(n: u32, l: u32, m: i32) -> Plot {
    let mut x_vals = Vec::new();
    let mut y_vals = Vec::new();
    let mut z_vals = Vec::new();
    let mut intensity = Vec::new();

    let steps = 50;
    let max_r = 10.0;

    for i in 0..=steps {
        let theta = PI * i as f64 / steps as f64;
        for j in 0..=steps {
            let phi = 2.0 * PI * j as f64 / steps as f64;
            for k in 0..=steps {
                let r = max_r * k as f64 / steps as f64;
                let radial = radial_wavefunction(n, l, r);
                let spherical = spherical_harmonic(l, m, theta, phi);
                let prob_density = radial.powi(2) * spherical.norm_sqr();

                let x = r * theta.sin() * phi.cos();
                let y = r * theta.sin() * phi.sin();
                let z = r * theta.cos();

                x_vals.push(x);
                y_vals.push(y);
                z_vals.push(z);
                intensity.push(prob_density);
            }
        }
    }

    // let trace = Surface::<f64, f64, f64>::new(vec![z_vals, y_vals, x_vals])
    //     // .z(intensity)
    //     .connect_gaps(true)
    //     // .reversescale(true)
    //     .show_scale(false)
    //     // .opacity(intensity);
    //     .surface_color(intensity)
        // .color_scale(ColorScale::try_from(intensity).unwrap());
    // .color_scale(ColorScale::try_from(intensity).unwrap());

    let trace = Surface::new(z_vals)
        .x(x_range)
        .y(y_range)
        .color_scale(ColorScale::Jet);
    
    let mut plot = Plot::new();
    plot.add_trace(trace);
    plot
}

fn main() -> Result<(), eframe::Error> {
    eframe::run_native(
        "Quantum Orbitals",
        eframe::NativeOptions::default(),
        Box::new(|_| Ok(Box::new(OrbitalApp::default()))),
    )
}
