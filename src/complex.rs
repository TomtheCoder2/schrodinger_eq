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

impl std::ops::Sub for Complex<f64> {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        Self {
            re: self.re - other.re,
            im: self.im - other.im,
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

impl std::ops::Mul<Complex<f64>> for Complex<f64> {
    type Output = Self;

    fn mul(self, other: Self) -> Self {
        Self {
            re: self.re * other.re - self.im * other.im,
            im: self.re * other.im + self.im * other.re,
        }
    }
}

impl std::ops::AddAssign for Complex<f64> {
    fn add_assign(&mut self, other: Self) {
        self.re += other.re;
        self.im += other.im;
    }
}

impl Complex<f64> {
    pub(crate) fn i() -> Self {
        Self { re: 0.0, im: 1.0 }
    }
}