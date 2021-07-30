#include "BMCSim.h"
#include "ExternalSequence.h"
#include "BlochMcConnellSolver.h"


BMCSim::BMCSim(SimulationParameters &SimPars, const char * SeqName) {
    sp = &SimPars;
    seq.load(SeqName);
    sp->SetExternalSequence(seq);
    InitSolver();
}

BMCSim::~BMCSim() {
    delete solver;
}

void BMCSim::SetSimulationParameters(SimulationParameters &SimPars) {
    sp = &SimPars;
}

SimulationParameters BMCSim::GetSimulationParameters() {
    return *sp;
}

Eigen::MatrixXd BMCSim::GetFinalMagnetizationVectors() {
    return sp->GetFinalMagnetizationVectors();
}

void BMCSim::InitSolver() {
    switch (sp->GetNumberOfCESTPools()) {
        case 0: // only water
            if (sp->IsMTActive())
                solver = new  BlochMcConnellSolver<4>(*sp);
            else
                solver = new BlochMcConnellSolver<3>(*sp);
            break;
        case 1: // one cest pool
            if (sp->IsMTActive())
                solver = new  BlochMcConnellSolver<7>(*sp);
            else
                solver = new BlochMcConnellSolver<6>(*sp);
            break;
        case 2: // two cest pools
            if (sp->IsMTActive())
                solver = new  BlochMcConnellSolver<10>(*sp);
            else
                solver = new BlochMcConnellSolver<9>(*sp);
            break;
        case 3: // three cest pools
            if (sp->IsMTActive())
                solver = new  BlochMcConnellSolver<13>(*sp);
            else
                solver = new BlochMcConnellSolver<12>(*sp);
            break;
        default:
            solver = new BlochMcConnellSolver<Eigen::Dynamic>(*sp); // > three pools
            break;
    }
}

void BMCSim::RunSimulation() {
    solver->UpdateSimulationParameters(*sp);
    solver->RunSimulation(*sp);
}
