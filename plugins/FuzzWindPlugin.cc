/*
 * Copyright (C) 2016 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/
#include "gazebo/common/Assert.hh"
#include "gazebo/common/Events.hh"
#include "../include/FuzzWindPlugin.hh"

using namespace gazebo;

GZ_REGISTER_WORLD_PLUGIN(FuzzWindPlugin)

/////////////////////////////////////////////////
void FuzzWindPlugin::Load(physics::WorldPtr _world, sdf::ElementPtr _sdf)
{
	world_ = _world;
	double wind_gust_start = kDefaultWindGustStart;
	double wind_gust_duration = kDefaultWindGustDuration;

	if(_sdf->HasElement("frameId")) {
		frame_id_ = _sdf->Get<std::string>("frameId");
	}
	if(_sdf->HasElement("linkName")) {
		link_name_ = _sdf->Get<std::string>("linkName");
	}
	if(_sdf->HasElement("modelName")) {
		model_name_ = _sdf->Get<std::string>("modelName");
	}
	if(_sdf->HasElement("windForceMean")) {
		wind_force_mean_ = _sdf->Get<double>("windForceMean");
	}
	if(_sdf->HasElement("windForceVariance")) {
		wind_force_variance_ = _sdf->Get<double>("windForceVariance");
	}
	if(_sdf->HasElement("windDirection")) {
		wind_direction_ = _sdf->Get<ignition::math::Vector3d>("windDirection");
	}
	if(_sdf->HasElement("windGustStart")) {
		wind_gust_start = _sdf->Get<double>("windGustStart");
	}
	if(_sdf->HasElement("windGustDuration")) {
		wind_gust_duration = _sdf->Get<double>("windGustDuration");
	}
	if(_sdf->HasElement("windGustForceMean")) {
		wind_gust_force_mean_ = _sdf->Get<double>("windGustForceMean");
	}
	if(_sdf->HasElement("windGustForceVariance")) {
		wind_gust_force_variance_ = _sdf->Get<double>("windGustForceVariance");
	}
	if(_sdf->HasElement("windGustDirection")) {
		wind_gust_direction_ = _sdf->Get<ignition::math::Vector3d>("windGustDirection");
	}
    if(_sdf->HasElement("xyz_offset")) {
	    xyz_offset_	= _sdf->Get<ignition::math::Vector3d>("xyz_offset");
	}

	wind_direction_.Normalize();
	wind_gust_direction_.Normalize();
	wind_gust_start_ = common::Time(wind_gust_start);
	wind_gust_end_ = common::Time(wind_gust_start + wind_gust_duration);

    physics::Model_V models = world_->GetModels();

    // Process each model.
    for (auto const &model : models)
    {
        //gzdbg << "Model: " << model->GetId() << " " << model->GetName() << "\n";
        //gzdbg << model->GetName().compare("copter_iris") << "\n";

		if(model->GetName().compare("copter_iris") == 0) {		// found model
			model_ = model;
		}	

        // Get all the links
        physics::Link_V links = model->GetLinks();

        // Process each link.
        for (auto const &link : links)
        {
            //gzdbg << link->GetName() << "\n";
            if(link->GetName().find(link_name_) != std::string::npos) {
                link_ = link;
            }   
            // Skip links for which the wind is disabled
        }
    }

    if (link_ == NULL)
        gzthrow("[gazebo_wind_plugin] Couldn't find specified link \"" << link_name_ << "\".");


    //link_ = model_->GetLink(link_name_);
    //if (link_ == NULL)
    //    gzthrow("[gazebo_wind_plugin] Couldn't find specified link \"" << link_name_ << "\".");

    gzdbg << "FUZZ WIND PLUGIN LOADED!! Link: " << link_->GetName() << "\n";
    gzdbg << "Wind Gust: [" << wind_gust_start_ << " " << wind_gust_end_ << "] " << "direction [" 
        << wind_gust_direction_ << "] wind_gust_force " << wind_gust_force_mean_ << " offset ["<< xyz_offset_ << "]\n";

    this->updateConnection = event::Events::ConnectWorldUpdateBegin(
            std::bind(&FuzzWindPlugin::OnUpdate, this));

}

/////////////////////////////////////////////////
void FuzzWindPlugin::OnUpdate()
{
    // Get the current simulation time.
    common::Time now = world_->GetSimTime();
    //gzdbg << now << ", " << world_->GetRealTime() << ", " << world_->GetStartTime() << "\n";

    // Calculate the wind force.
    double wind_strength = wind_force_mean_;
    math::Vector3 wind = wind_strength * wind_direction_;
    // Apply a force from the constant wind to the link.
    link_->AddForceAtRelativePosition(wind, xyz_offset_);

    math::Vector3 wind_gust(0, 0, 0);
    bool under_wind = false;
    //if(int(now.Double() * 1000) % 1000 == 0) {  // per second
    //    wind_gust_force_mean_ = -1 * wind_gust_force_mean_;
    //}
    // Calculate the wind gust force.
    if (now >= wind_gust_start_ && now < wind_gust_end_) {
        under_wind = true;
        double wind_gust_strength = wind_gust_force_mean_;
        wind_gust = wind_gust_strength * wind_gust_direction_;


        //physics::Link_V links = model_->GetLinks();
        //for (auto const &link : links)
        //{
		//	//if(int(now.Double() * 1000) % 1000 == 0) {  // per second
		//	//	gzdbg << "add wind to link: " << link->GetName() << "\n";
		//	//}
		//	link->AddRelativeForce(wind_gust);
        //}



        link_->AddForceAtRelativePosition(wind_gust, xyz_offset_);
        //link_->AddForceAtWorldPosition(wind_gust, xyz_offset_);
        //link_->AddForceAtWorldPosition(wind_gust, link_->GetWorldPose().pos);
        //link_->AddRelativeForce(wind_gust);


	//// Process each link.
    //for (auto const &link : links)
    //{
    //  // Skip links for which the wind is disabled
    //  if (!link->WindMode())
    //    continue;

    //  // Add wind velocity as a force to the body
    //  link->AddRelativeForce(link->GetInertial()->GetMass() *
    //      this->forceApproximationScalingFactor *
    //      (link->RelativeWindLinearVel() - link->GetRelativeLinearVel().Ign()));
    //}


        if(wind_gust_on == false) {
            gzdbg << "**** Wind Gust ON: " << wind_gust << " to " << link_->GetWorldPose().pos << "\n";
        }
        wind_gust_on = true;
    } else {
        if(wind_gust_on == true) {
            gzdbg << "**** Wind Gust OFF: " << wind_gust << " to " << link_->GetWorldPose().pos << "\n";
        }
        wind_gust_on = false;
    }

    if(int(now.Double() * 1000) % 1000 == 0) {  // per second
        gzdbg << "WIND: [" << std::setprecision(0) << std::fixed << now.Double() << "|" << wind_gust_start_.Double() << "-" << wind_gust_end_.Double() << "] wind [" << wind_gust << std::setprecision(1) << std::fixed << "] off " << xyz_offset_ << " (" << under_wind << ")\n";
        gzdbg << "Position: " << std::setprecision(2) << std::fixed << link_->GetParentModel()->GetWorldPose() << "\n"; 
    }
}
