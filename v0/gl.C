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
   TGeoManager::Import("protodunevd_v4_refactored_nowires.gdml");
 //TGeoManager::Import("pd_vd_crt.gdml");

  TGeoNode* world = gGeoManager->GetTopNode();

  TGeoNode *det = world->GetDaughter(0);
  // TGeoNode *cryo = det->GetDaughter(0);
  TEveGeoTopNode* top = new TEveGeoTopNode(gGeoManager, det);

  gEve->AddGlobalElement(top);


  // int nDaughters = det->GetNdaughters();
  // for (int i=0; i<nDaughters; i++) {
  //   TGeoNode *node = det->GetDaughter(i);
  //   TString name(node->GetName());
  //   if (name.Contains("Foam") || name.Contains("Steel") 
  //       || name.Contains("Concrete") || name.Contains("Neck")) {
  //     node->SetInvisible();
  //     node->SetAllInvisible();
  //   }
  // }

  // nDaughters = cryo->GetNdaughters();
  // for (int i=0; i<nDaughters; i++) {
  //   TGeoNode *node = cryo->GetDaughter(i);
  //   TString name(node->GetName());
  //   if (name.Contains("TPC") || name.Contains("Steel") 
  //       || name.Contains("Concrete") || name.Contains("Argon")) {
  //     node->SetInvisible();
  //     node->SetAllInvisible();
  //   }
  // }

  // // cryo->GrabFocus();

  gEve->Redraw3D(kTRUE);

}
