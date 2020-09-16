//  SimulationParameters.h
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

#pragma once

//!  Water Pool class. 
/*!
  Class containing  relaxation parameters and fraction of Pools
*/
class WaterPool
{
public:
	//! Default Constructor
	WaterPool();

	//! Constructor
	WaterPool(double nR1, double nR2, double nf);

	//! Default destructor
	~WaterPool();

	//! Get R1
	const double GetR1();

	//! Get R2
	const double GetR2();

	//! Get f
	const double GetFraction();

	//! Set R1
	void SetR1(double nR1);

	//! Set R2
	void SetR2(double nR2);

	//! Set f
	void SetFraction(double nf);


protected:
	double R1; /*!< 1/T1 [Hz]  */
	double R2; /*!< 1/T1 [Hz]  */
	double f; /*!< proton fraction  */
};

