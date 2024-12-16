#include "TEveManager.h"
#include "TEveGeoNode.h"

#include "TGeoManager.h"
#include "TGeoNode.h"
#include "TGeoVolume.h"
#include "TGeoMedium.h"

void gl()
{
  gSystem->IgnoreSignal(kSigSegmentationViolation, true);
  TEveManager::Create();
  // TGeoManager::Import("lbne35t4apa.gdml");
  //TGeoManager::Import("lbne35t4apa_v3_nowires.gdml");
  // TGeoManager::Import("lbne35t4apa_v3.gdml");
  TGeoManager::Import("protodune.gdml");

  TGeoNode* world = gGeoManager->GetTopNode();

  TGeoNode *det = world->GetDaughter(0);
  TGeoNode *cryo = det->GetDaughter(0);

  TGeoNode *argon = cryo->GetDaughter(1);

  TEveGeoTopNode* top = new TEveGeoTopNode(gGeoManager, det);
  gEve->AddGlobalElement(top);


   int nDaughters = det->GetNdaughters();
   for (int i=0; i<nDaughters; i++) {
     TGeoNode *node = det->GetDaughter(i);
     TString name(node->GetName());
    //  cout << i << " " << name << endl;

  //   if (name.Contains("Foam") || name.Contains("Steel") 
  //       || name.Contains("Concrete") || name.Contains("Neck")) {
  //     node->SetInvisible();
  //     node->SetAllInvisible();
  //   }
   }

  nDaughters = cryo->GetNdaughters();
  for (int i=0; i<nDaughters; i++) {
    TGeoNode *node = cryo->GetDaughter(i);
    TString name(node->GetName());
     cout << i << " " << name << endl;
     if (name.Contains("steel") || name.Contains("argon")) {
       node->SetInvisible();
       //node->SetAllInvisible();
     } 
  //       || name.Contains("Concrete") || name.Contains("Argon")) {
  //     node->SetInvisible();
  //     node->SetAllInvisible();
  //   }
   }

nDaughters = argon->GetNdaughters();
for (int i = 0; i < nDaughters; i++) {
    TGeoNode *node = argon->GetDaughter(i);
    TString name(node->GetName());

    // if (name.Contains("gasAr")) {
    //     node->SetInvisible();  // Hide this node and its descendants
    // }

    if (name.Contains("volCathodeArapucaMesh")) {
        node->SetVisibility(kFALSE);  // Hide the parent node

        // int nChildren = node->GetNdaughters();
        // std::cout << "Number of daughters: " << nChildren << std::endl;

        // if (nChildren == 0) {
        //     std::cout << "No daughters found for volCathodeArapucaMesh" << std::endl;
        // }

        // Loop through the daughters and make them visible
        for (Int_t j = 0; j < node->GetNdaughters(); j++) {
            TGeoNode* daughter = node->GetDaughter(j);

            // Print volume information of the daughter node
            // if (daughter->GetVolume()) {
            //     daughter->GetVolume()->Print();
            // } else {
            //     std::cout << "Daughter volume is NULL" << std::endl;
            // }

            daughter->SetVisibility(kTRUE);  // Ensure each daughter is visible

            // Draw each daughter node separately
            // TEveGeoTopNode* eveNode = new TEveGeoTopNode(gGeoManager, daughter);
            // gEve->AddGlobalElement(eveNode);
        }

        // Optionally print information for verification
       // node->GetVolume()->Print();
    }
}

argon->Draw("ogl");

// Redraw the scene to apply changes
gEve->Redraw3D(kTRUE);
//gEve->GetDefaultGLViewer()->ResetCameras();

}
