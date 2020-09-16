//  SimulationParameters.cpp
/*!
Container class for all simulation related parameters that need to get passed between classes and functions

kai.herz@tuebingen.mpg.de

Copyright 2020 Kai Herz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/


#include "SimulationParameters.h"


// Water Pool Function Definitions ////

//! Default Constructor
WaterPool::WaterPool() : R1(0), R2(0), f(0) {}

//! Constructor
/*!
  \param nR1 R1 of water pool [1/s]
  \param nR2 R2 of water pool [1/s]
  \param nf fraction of water pool
*/
WaterPool::WaterPool(double nR1, double nR2, double nf) : R1(nR1), R2(nR2), f(nf) {}

//! Default destructor
WaterPool::~WaterPool() {}

//! Get R1
/*! \return 1/T1 of pool */
const double WaterPool::GetR1() { return R1; }

//! Get R2
/*! \return 1/T2 of pool */
const double WaterPool::GetR2() { return R2; }

//! Get f
/*! \return fraction of pool */
const double WaterPool::GetFraction() { return f; }

//! Set R1
/*! \param new 1/T1 of pool */
void WaterPool::SetR1(double nR1) { R1 = nR1; }

//! Set R2
/*! \param new 1/T2 of pool */
void WaterPool::SetR2(double nR2) { R2 = nR2; }

//! Set f
/*! \param new fraction of pool */
void WaterPool::SetFraction(double nf) { f = nf; }


