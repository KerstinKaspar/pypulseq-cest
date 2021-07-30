#include "SimulationParameters.h"
#include "BlochMcConnellSolver.h"

class BMCSim
{
public:
    //! Default constructor
	BMCSim() {}

    //! Constructor
	BMCSim(SimulationParameters &SimPars, const char * SeqName);

	//! Default destructor
	~BMCSim();

	//! Set simulations parameters object
	void SetSimulationParameters(SimulationParameters &SimPars);

	//! Get simulations parameters object
	SimulationParameters GetSimulationParameters();

	//! Get magnetization vector after simulation
	Eigen::MatrixXd GetFinalMagnetizationVectors();

	//! Run Simulation
	void RunSimulation();

private:
	ExternalSequence seq;
	SimulationParameters* sp;
	BlochMcConnellSolverBase* solver;

	//! Init solver
	void InitSolver();
};
