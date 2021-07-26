#include "SimulationParameters.h"
#include "BlochMcConnellSolver.h"

class BMCSim
{
public:
    //! Default constructor
	BMCSim() {}

    //! Python constructor
	BMCSim(SimulationParameters &SimPars, const char * SeqName);

	//! MATLAB constructor

	//! Default destructor
	~BMCSim() {}

	//! Set external sequence object
	void SetSimulationParameters(SimulationParameters &SimPars);

	//! Init solver
	void InitSolver();

	//! Update SimulationParameters
	void UpdateSimulationParameters(SimulationParameters &SimPars);

	//! Run Simulation
	void RunSimulation();

	//! End Simulation
	void EndSimulation();

private:
	ExternalSequence seq;
	SimulationParameters* sp;
	BlochMcConnellSolverBase* solver;
};
