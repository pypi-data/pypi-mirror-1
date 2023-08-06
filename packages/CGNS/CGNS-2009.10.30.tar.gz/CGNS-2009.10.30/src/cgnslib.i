/***************************************************************************
#*   Copyright (C) 2009 by Steve Walter, Oliver Borm, Franz Blaim          *
#*   steve.walter@mytum.de, oli.borm@web.de, franz.blaim@gmx.de            *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, write to the                         *
#*   Free Software Foundation, Inc.,                                       *
#*   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#***************************************************************************

# Author: Steve Walter, Franz Blaim, Oliver Borm
# Date: March 2009
*/

%module CGNS
%{
#include "cgnslib.h"

void charP2String(char *in, char *out)
{
	sprintf(out,"%s",in);
}

%}

%include "carrays.i"
%include "cstring.i"
%include "cgnslib.h"
%include "cpointer.i"

// Conversion of a char pointer to an string
%cstring_bounded_output(char *out, 1024);
void charP2String(char *in, char *out);

//IntPointer wrapper
//%array_functions(int,intArray)
//%array_functions(float,floatArray)
%array_class(int,intArray)
%array_class(float,floatArray)
%array_class(double,doubleArray)
//%array_class(char,charArray)
%pointer_class(int, intp);
%pointer_class(float,floatp);
%pointer_class(double,doublep);
%pointer_class(char,charp);

%pointer_class(ZoneType_t,ZoneType_tp);
%pointer_class(AngleUnits_t,AngleUnits_tp);
%pointer_class(MassUnits_t,MassUnits_tp);
%pointer_class(LengthUnits_t,LengthUnits_tp);
%pointer_class(TimeUnits_t,TimeUnits_tp);
%pointer_class(TemperatureUnits_t,TemperatureUnits_tp);
%pointer_class(ElectricCurrentUnits_t,ElectricCurrentUnits_tp);
%pointer_class(LuminousIntensityUnits_t,LuminousIntensityUnits_tp);
%pointer_class(DataClass_t,DataClass_tp);
%pointer_class(GridLocation_t,GridLocation_tp);
%pointer_class(GridConnectivityType_t,GridConnectivityType_tp);
%pointer_class(BCDataType_t,BCDataType_tp);
%pointer_class(PointSetType_t,PointSetType_tp);
%pointer_class(GoverningEquationsType_t, GoverningEquationsType_tp);
%pointer_class( ModelType_t, ModelType_tp);
%pointer_class(BCType_t, BCType_tp);
%pointer_class(DataType_t, DataType_tp);
%pointer_class( ElementType_t ,ElementType_tp);
%pointer_class(ArbitraryGridMotionType_t, ArbitraryGridMotionType_tp);
%pointer_class(SimulationType_t,SimulationType_tp);
%pointer_class( WallFunctionType_t,  WallFunctionType_tp);
%pointer_class( AreaType_t, AreaType_tp);
%pointer_class( AverageInterfaceType_t , AverageInterfaceType_tp);
