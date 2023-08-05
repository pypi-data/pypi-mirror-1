/* Copyright 2005 Robert Kern (robert.kern@gmail.com)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include <math.h>
#include "distributions.h"
#include "mconf.h"
#include <stdio.h>

#ifndef min
#define min(x,y) ((x<y)?x:y)
#define max(x,y) ((x>y)?x:y)
#endif

double rk_normal(rk_state *state, double loc, double scale)
{
    return loc + scale*rk_gauss(state);
}

double rk_standard_exponential(rk_state *state)
{
    return -log(rk_double(state));
}

double rk_exponential(rk_state *state, double scale)
{
    return scale * rk_standard_exponential(state);
}

double rk_uniform(rk_state *state, double loc, double scale)
{
    return loc + scale*rk_double(state);
}

#define LOG4 1.3862943611198906
#define ONELOG92 2.5040773967762742

double rk_standard_gamma(rk_state *state, double shape)
{
    double b, c, lam;
    double U, V, X, Y, Z, R;

    if (shape == 1.0)
    {
        return rk_standard_exponential(state);
    }
    else if (shape < 1.0)
    {
        while (1)
        {
            U = rk_double(state);
            V = rk_standard_exponential(state);
            if (U <= 1.0 - shape)
            {
                X = pow(U, 1./shape);
                if (X <= V)
                {
                    return X;
                }
            }
            else
            {
                Y = -log((1-U)/shape);
                X = pow(1.0 - shape + shape*Y, 1./shape);
                if (X <= (V + Y))
                {
                    return X;
                }
            }
        }
    }
    else
    {
        b = shape - LOG4;
        lam = sqrt(2.0*shape - 1.0);
        c = shape + lam;
        
        while (1)
        {
            U = rk_double(state);
            V = rk_double(state);
            Y = log(V/(1.0-V))/lam;
            X = shape*exp(Y); 
            Z = U*V*V;
            R = b + c*Y - X;
            if ((R >= 4.5*Z - ONELOG92) || (R >= log(Z)))
            {
                break;
            }
        }
        return X;
    }
}

#undef LOG4
#undef ONELOG92

double rk_gamma(rk_state *state, double shape, double scale)
{
    return scale * rk_standard_gamma(state, shape);
}

double rk_beta(rk_state *state, double a, double b)
{
    double Ga, Gb;

    if ((a <= 1.0) && (b <= 1.0))
    {
        double U, V, X, Y;
        /* Use Jonk's algorithm */

        while (1)
        {
            U = rk_double(state);
            V = rk_double(state);
            X = pow(U, 1.0/a);
            Y = pow(V, 1.0/b);

            if ((X + Y) <= 1.0)
            {
                return X;
            }
        }
    }
    else
    {
        Ga = rk_standard_gamma(state, a);
        Gb = rk_standard_gamma(state, b);
        return Ga/(Ga + Gb);
    }
}

double rk_chisquare(rk_state *state, double df)
{
    return 2.0*rk_standard_gamma(state, df/2.0);
}

double rk_noncentral_chisquare(rk_state *state, double df, double nonc)
{
    double Chi2, N;

    Chi2 = rk_chisquare(state, df-1);
    N = rk_gauss(state) + sqrt(nonc);
    return Chi2 + N*N;
}

double rk_f(rk_state *state, double dfnum, double dfden)
{
    return rk_chisquare(state, dfnum) / rk_chisquare(state, dfden);
}

double rk_noncentral_f(rk_state *state, double dfnum, double dfden, double nonc)
{
    return ((rk_noncentral_chisquare(state, dfnum, nonc)*dfden) /
            (rk_chisquare(state, dfden)*dfnum));
}

long rk_binomial_btpe(rk_state *state, long n, double p)
{
    double r,q,fm,p1,xm,xl,xr,c,laml,lamr,p2,p3,p4;
    double a,u,v,s,F,rho,t,A,nrq,x1,x2,f1,f2,z,z2,w,w2,x;
    long m,y,k,i;

    if (!(state->has_binomial) || 
         (state->nsave != n) ||
         (state->psave != p))
    {
        /* initialize */
        state->nsave = n;
        state->psave = p;
        state->has_binomial = 1;
        state->r = r = min(p, 1.0-p);
        state->q = q = 1.0 - r;
        state->fm = fm = n*r+r;
        state->m = m = (long)floor(state->fm);
        state->p1 = p1 = floor(2.195*sqrt(n*r*q)-4.6*q) + 0.5;
        state->xm = xm = m + 0.5;
        state->xl = xl = xm - p1;
        state->xr = xr = xm + p1;
        state->c = c = 0.134 + 20.5/(15.3 + m);
        a = (fm - xl)/(fm-xl*r);
        state->laml = laml = a*(1.0 + a/2.0);
        a = (xr - fm)/(xr*q);
        state->lamr = lamr = a*(1.0 + a/2.0);
        state->p2 = p2 = p1*(1.0 + 2.0*c);
        state->p3 = p3 = p2 + c/laml;
        state->p4 = p4 = p3 + c/lamr;
    }
    else
    {
        r = state->r;
        q = state->q;
        fm = state->fm;
        m = state->m;
        p1 = state->p1;
        xm = state->xm;
        xl = state->xl;
        xr = state->xr;
        c = state->c;
        laml = state->laml;
        lamr = state->lamr;
        p2 = state->p2;
        p3 = state->p3;
        p4 = state->p4;
    }

  /* sigh ... */
  Step10:
    nrq = n*r*q;
    u = rk_double(state)*p4;
    v = rk_double(state);
    if (u > p1) goto Step20;
    y = (long)floor(xm - p1*v + u);
    goto Step60;

  Step20:
    if (u > p2) goto Step30;
    x = xl + (u - p1)/c;
    v = v*c + 1.0 - fabs(m - x + 0.5)/p1;
    if (v > 1.0) goto Step10;
    y = (long)floor(x);
    goto Step50;

  Step30:
    if (u > p3) goto Step40;
    y = (long)floor(xl + log(v)/laml);
    if (y < 0) goto Step10;
    v = v*(u-p2)*laml;
    goto Step50;

  Step40:
    y = (int)floor(xr - log(v)/lamr);
    if (y > n) goto Step10;
    v = v*(u-p3)*lamr;

  Step50:
    k = fabs(y - m);
    if ((k > 20) && (k < ((nrq)/2.0 - 1))) goto Step52;

    Step51:
    s = r/q;
    a = s*(n+1);
    F = 1.0;
    if (m < y)
    {
        for (i=m; i<=y; i++)
        {
            F *= (a/i - s);
        }
    }
    else if (m > y)
    {
        for (i=y; i<=m; i++)
        {
            F /= (a/i - s);
        }
    }
    else
    {
        if (v > F) goto Step10;
        goto Step60;
    }

    Step52:
    rho = (k/(nrq))*((k*(k/3.0 + 0.625) + 0.16666666666666666)/nrq + 0.5);
    t = -k*k/(2*nrq);
    A = log(v);
    if (A < (t - rho)) goto Step60;
    if (A > (t + rho)) goto Step10;

    Step53:
    x1 = y+1;
    f1 = m+1;
    z = n+1-m;
    w = n-y+1;
    x2 = x1*x1;
    f2 = f1*f1;
    z2 = z*z;
    w2 = w*w;
    if (A > (xm*log(f1/x1)
           + (n-m+0.5)*log(z/w)
           + (y-m)*log(w*r/(x1*q))
           + (13680.-(462.-(132.-(99.-140./f2)/f2)/f2)/f2)/f1/166320.
           + (13680.-(462.-(132.-(99.-140./z2)/z2)/z2)/z2)/z/166320.
           + (13680.-(462.-(132.-(99.-140./x2)/x2)/x2)/x2)/x1/166320.
           + (13680.-(462.-(132.-(99.-140./w2)/w2)/w2)/w2)/w/166320.))
    {
        goto Step10;
    }

  Step60:
    if (p > 0.5)
    {
        y = n - y;
    }

    return y;
}

long rk_binomial_waiting(rk_state *state, long n, double p)
{
    double q, E, Sum;
    long X;

    q = -log(1.0 - p);

    X = 0;
    Sum = 0.0;

    while (Sum <= q)
    {
        if (X == n)
        {
            X += 1;
            break;
        }
        E = rk_standard_exponential(state);
        Sum += E / (n - X);
        X++;
    }
    return X-1;
}

long rk_binomial(rk_state *state, long n, double p)
{
    double q;

    if (p <= 0.5)
    {
        if (p*n <= 30.0)
        {
            return rk_binomial_waiting(state, n, p);
        }
        else
        {
            return rk_binomial_btpe(state, n, p);
        }
    }
    else
    {
        q = 1.0-p;
        if (q*n <= 30.0)
        {
            return n - rk_binomial_waiting(state, n, q);
        }
        else
        {
            return n - rk_binomial_btpe(state, n, q);
        }
    }

}

long rk_negative_binomial(rk_state *state, long n, double p)
{
    double Y;

    Y = rk_gamma(state, n, (1-p)/p);
    return rk_poisson(state, Y);
}

long _rk_poisson_bad(rk_state *state, double lam)
{
    long mu;
    double delta, delta_2, c1, c2, c3, c4, c, loglammu, qx;
    double U, E, N, Y, W, V;
    long X;


    mu = (long)floor(lam);
    delta = max(6.0, min(mu, sqrt(2*mu*log(128*mu/M_PI))));
    delta_2 = delta/2.0;
    c1 = sqrt(M_PI_2*mu);
    c2 = c1 + sqrt(M_PI_2*(mu + delta_2))*exp(1./(2*mu+delta));
    c3 = c2 + 2;
    c4 = c3 + exp(1./78.);
    c = c4 + (2.*mu + delta)/delta_2*exp(-delta*(1+delta_2)/(2*mu+delta));
    loglammu = log(lam/mu);

    while (1)
    {
        U = c*rk_double(state);
        E = rk_standard_exponential(state);

        if (U <= c1)
        {
            N = rk_gauss(state);
            Y = -fabs(N)*sqrt(mu)-1;
            X = (long)floor(Y);
            W = -N*N/2.0 - E - X*loglammu;
            if (X < -mu)
            {
                /* W = INFINITY; */
                continue;
            }
        }
        else if (U <= c2)
        {
            N = rk_gauss(state);
            Y = 1 + fabs(N)*sqrt(mu+delta_2);
            X = (long)ceil(Y);
            W = (-Y*Y+2*Y)/(2*mu+delta) - E - X*loglammu;
            if (X > delta)
            {
                /* W = INFINITY; */
                continue;
            }
        }
        else if (U <= c3)
        {
            X = 0;
            W = -E;
        }
        else if (U <= c4)
        {
            X = 1;
            W = -E-loglammu;
        }
        else
        {
            V = rk_standard_exponential(state);
            Y = delta + V/delta_2*(2*mu+delta);
            X = (long)ceil(Y);
            W = -(1.0+Y/2.0)*delta/(2*mu+delta) - E - X*loglammu;
        }

        qx = X*log(mu) - lgam(mu+X+1) + lgam(mu+1);
        if (W <= qx) break;
    }
    return X;
}

long rk_poisson_mult(rk_state *state, double lam)
{
    long X;
    double prod, U, enlam;

    enlam = exp(-lam);
    X = 0;
    prod = 1.0;
    while (1)
    {
        U = rk_double(state);
        prod *= U;
        if (prod > enlam)
        {
            X += 1;
        }
        else
        {
            return X;
        }
    }
}

#define LS2PI 0.91893853320467267
#define TWELFTH 0.083333333333333333333333
long rk_poisson_ptrs(rk_state *state, double lam)
{
    static double lgam9[10] = {0.0,
                               0.0,
                               0.69314718055994528623,
                               1.79175946922805495731,
                               3.17805383034794575181,
                               4.78749174278204581157,
                               6.57925121201010121297,
                               8.52516136106541466688,
                               10.60460290274525085863,
                               12.80182748008146909058};
    long k;
    double U, V, slam, loglam, a, b, invalpha, vr, us;

    slam = sqrt(lam);
    loglam = log(lam);
    b = 0.931 + 2.53*slam;
    a = -0.059 + 0.02483*b;
    invalpha = 1.1239 + 1.1328/(b-3.4);
    vr = 0.9277 - 3.6224/(b-2);

    while (1)
    {
        U = rk_double(state) - 0.5;
        V = rk_double(state);
        us = 0.5 - fabs(U);
        k = (long)floor((2*a/us + b)*U + lam + 0.43);
        if ((us >= 0.07) && (V <= vr))
        {
            return k;
        }
        if ((k < 0) ||
            ((us < 0.013) && (V > us)))
        {
            continue;
        }
        if ((log(V) + log(invalpha) - log(a/(us*us)+b)) <=
            (-lam + k*loglam - lgam(k+1)))
        {
            return k;
        }

        
    }

}

long rk_poisson(rk_state *state, double lam)
{
    if (lam >= 10)
    {
        return rk_poisson_ptrs(state, lam);
    }
    else
    {
        return rk_poisson_mult(state, lam);
    }
}
