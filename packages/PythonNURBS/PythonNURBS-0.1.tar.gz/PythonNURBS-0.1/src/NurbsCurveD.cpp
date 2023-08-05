/**************************************************************************
*   Copyright (C) 2008-2008 by Franz Blaim, Oliver Borm                   *
*   franz.blaim@gmx.de, oli.borm@web.de                                   *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
*   This program is distributed in the hope that it will be useful,       *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU General Public License for more details.                          *
*                                                                         *
*   You should have received a copy of the GNU General Public License     *
*   along with this program; if not, write to the                         *
*   Free Software Foundation, Inc.,                                       *
*   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
***************************************************************************/

/** Author: Franz Blaim, Oliver Borm
 Date: February 2008
*/

// Boost Includes ==============================================================
#include <boost/python.hpp>
#include <boost/cstdint.hpp>

// Includes ====================================================================
#include <nurbs++/nurbsS.h>

// Using =======================================================================
using namespace boost::python;

// Declarations ================================================================
namespace  {

struct NurbsCurveArray2Dd_Wrapper: PLib::NurbsCurveArray<double,2>
{
    NurbsCurveArray2Dd_Wrapper(PyObject* py_self_, const PLib::NurbsCurveArray<double,2>& p0):
        PLib::NurbsCurveArray<double,2>(p0), py_self(py_self_) {}

    NurbsCurveArray2Dd_Wrapper(PyObject* py_self_, PLib::NurbsCurve<double,2>* p0, int p1):
        PLib::NurbsCurveArray<double,2>(p0, p1), py_self(py_self_) {}

    NurbsCurveArray2Dd_Wrapper(PyObject* py_self_):
        PLib::NurbsCurveArray<double,2>(), py_self(py_self_) {}

    void resize(int p0) {
        call_method< void >(py_self, "resize", p0);
    }

    void default_resize(int p0) {
        PLib::NurbsCurveArray<double,2>::resize(p0);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurveArray2Dd_writePS_overloads_1_5, writePS, 1, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurveArray2Dd_writePSp_overloads_3_7, writePSp, 3, 7)

struct NurbsCurveArray3Dd_Wrapper: PLib::NurbsCurveArray<double,3>
{
    NurbsCurveArray3Dd_Wrapper(PyObject* py_self_, const PLib::NurbsCurveArray<double,3>& p0):
        PLib::NurbsCurveArray<double,3>(p0), py_self(py_self_) {}

    NurbsCurveArray3Dd_Wrapper(PyObject* py_self_, PLib::NurbsCurve<double,3>* p0, int p1):
        PLib::NurbsCurveArray<double,3>(p0, p1), py_self(py_self_) {}

    NurbsCurveArray3Dd_Wrapper(PyObject* py_self_):
        PLib::NurbsCurveArray<double,3>(), py_self(py_self_) {}

    void resize(int p0) {
        call_method< void >(py_self, "resize", p0);
    }

    void default_resize(int p0) {
        PLib::NurbsCurveArray<double,3>::resize(p0);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurveArray3Dd_writePS_overloads_1_5, writePS, 1, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurveArray3Dd_writePSp_overloads_3_7, writePSp, 3, 7)

struct NurbsCurve2Dd_Wrapper: PLib::NurbsCurve<double,2>
{
    NurbsCurve2Dd_Wrapper(PyObject* py_self_):
        PLib::NurbsCurve<double,2>(), py_self(py_self_) {}

    NurbsCurve2Dd_Wrapper(PyObject* py_self_, const PLib::NurbsCurve<double,2>& p0):
        PLib::NurbsCurve<double,2>(p0), py_self(py_self_) {}

    NurbsCurve2Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::HPoint_nD<double, 2> >& p0, const PLib::Vector<double>& p1):
        PLib::NurbsCurve<double,2>(p0, p1), py_self(py_self_) {}

    NurbsCurve2Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::HPoint_nD<double, 2> >& p0, const PLib::Vector<double>& p1, int p2):
        PLib::NurbsCurve<double,2>(p0, p1, p2), py_self(py_self_) {}

    NurbsCurve2Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::Point_nD<double, 2> >& p0, const PLib::Vector<double>& p1, const PLib::Vector<double>& p2):
        PLib::NurbsCurve<double,2>(p0, p1, p2), py_self(py_self_) {}

    NurbsCurve2Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::Point_nD<double, 2> >& p0, const PLib::Vector<double>& p1, const PLib::Vector<double>& p2, int p3):
        PLib::NurbsCurve<double,2>(p0, p1, p2, p3), py_self(py_self_) {}

    void reset(const PLib::Vector<PLib::HPoint_nD<double, 2> >& p0, const PLib::Vector<double>& p1, int p2) {
        call_method< void >(py_self, "reset", p0, p1, p2);
    }

    void default_reset(const PLib::Vector<PLib::HPoint_nD<double, 2> >& p0, const PLib::Vector<double>& p1, int p2) {
        PLib::NurbsCurve<double,2>::reset(p0, p1, p2);
    }

    PLib::HPoint_nD<double,2> hpointAt(double p0, int p1) const {
        return call_method< PLib::HPoint_nD<double,2> >(py_self, "hpointAt", p0, p1);
    }

    PLib::HPoint_nD<double,2> default_hpointAt(double p0, int p1) const {
        return PLib::NurbsCurve<double,2>::hpointAt(p0, p1);
    }

    void deriveAtH(double p0, int p1, PLib::Vector<PLib::HPoint_nD<double, 2> >& p2) const {
        call_method< void >(py_self, "deriveAtH", p0, p1, p2);
    }

    void default_deriveAtH(double p0, int p1, PLib::Vector<PLib::HPoint_nD<double, 2> >& p2) const {
        PLib::NurbsCurve<double,2>::deriveAtH(p0, p1, p2);
    }

    void deriveAt(double p0, int p1, PLib::Vector<PLib::Point_nD<double, 2> >& p2) const {
        call_method< void >(py_self, "deriveAt", p0, p1, p2);
    }

    void default_deriveAt(double p0, int p1, PLib::Vector<PLib::Point_nD<double, 2> >& p2) const {
        PLib::NurbsCurve<double,2>::deriveAt(p0, p1, p2);
    }

    double minKnot() const {
        return call_method< double >(py_self, "minKnot");
    }

    double default_minKnot() const {
        return PLib::NurbsCurve<double,2>::minKnot();
    }

    double maxKnot() const {
        return call_method< double >(py_self, "maxKnot");
    }

    double default_maxKnot() const {
        return PLib::NurbsCurve<double,2>::maxKnot();
    }

    void degreeElevate(int p0) {
        call_method< void >(py_self, "degreeElevate", p0);
    }

    void default_degreeElevate(int p0) {
        PLib::NurbsCurve<double,2>::degreeElevate(p0);
    }

    void modKnot(const PLib::Vector<double>& p0) {
        call_method< void >(py_self, "modKnot", p0);
    }

    void default_modKnot(const PLib::Vector<double>& p0) {
        PLib::NurbsCurve<double,2>::modKnot(p0);
    }

    int read(std::basic_ifstream<char,std::char_traits<char> >& p0) {
        return call_method< int >(py_self, "read", p0);
    }

    int default_read(std::basic_ifstream<char,std::char_traits<char> >& p0) {
        return PLib::NurbsCurve<double,2>::read(p0);
    }

    double minDist2(const PLib::Point_nD<double,2>& p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< double >(py_self, "minDist2", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    double default_minDist2_2(const PLib::Point_nD<double,2>& p0, double& p1) const {
        return PLib::ParaCurve<double,2>::minDist2(p0, p1);
    }

    double default_minDist2_3(const PLib::Point_nD<double,2>& p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,2>::minDist2(p0, p1, p2);
    }

    double default_minDist2_4(const PLib::Point_nD<double,2>& p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,2>::minDist2(p0, p1, p2, p3);
    }

    double default_minDist2_5(const PLib::Point_nD<double,2>& p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,2>::minDist2(p0, p1, p2, p3, p4);
    }

    double default_minDist2_6(const PLib::Point_nD<double,2>& p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,2>::minDist2(p0, p1, p2, p3, p4, p5);
    }

    double default_minDist2_7(const PLib::Point_nD<double,2>& p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,2>::minDist2(p0, p1, p2, p3, p4, p5, p6);
    }

    double default_minDist2_8(const PLib::Point_nD<double,2>& p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,2>::minDist2(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,2> minDistY(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< PLib::Point_nD<double,2> >(py_self, "minDistY", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,2> default_minDistY_2(double p0, double& p1) const {
        return PLib::ParaCurve<double,2>::minDistY(p0, p1);
    }

    PLib::Point_nD<double,2> default_minDistY_3(double p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,2>::minDistY(p0, p1, p2);
    }

    PLib::Point_nD<double,2> default_minDistY_4(double p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,2>::minDistY(p0, p1, p2, p3);
    }

    PLib::Point_nD<double,2> default_minDistY_5(double p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,2>::minDistY(p0, p1, p2, p3, p4);
    }

    PLib::Point_nD<double,2> default_minDistY_6(double p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,2>::minDistY(p0, p1, p2, p3, p4, p5);
    }

    PLib::Point_nD<double,2> default_minDistY_7(double p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,2>::minDistY(p0, p1, p2, p3, p4, p5, p6);
    }

    PLib::Point_nD<double,2> default_minDistY_8(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,2>::minDistY(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,2> minDistX(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< PLib::Point_nD<double,2> >(py_self, "minDistX", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,2> default_minDistX_2(double p0, double& p1) const {
        return PLib::ParaCurve<double,2>::minDistX(p0, p1);
    }

    PLib::Point_nD<double,2> default_minDistX_3(double p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,2>::minDistX(p0, p1, p2);
    }

    PLib::Point_nD<double,2> default_minDistX_4(double p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,2>::minDistX(p0, p1, p2, p3);
    }

    PLib::Point_nD<double,2> default_minDistX_5(double p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,2>::minDistX(p0, p1, p2, p3, p4);
    }

    PLib::Point_nD<double,2> default_minDistX_6(double p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,2>::minDistX(p0, p1, p2, p3, p4, p5);
    }

    PLib::Point_nD<double,2> default_minDistX_7(double p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,2>::minDistX(p0, p1, p2, p3, p4, p5, p6);
    }

    PLib::Point_nD<double,2> default_minDistX_8(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,2>::minDistX(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,2> minDistZ(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< PLib::Point_nD<double,2> >(py_self, "minDistZ", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,2> default_minDistZ_2(double p0, double& p1) const {
        return PLib::ParaCurve<double,2>::minDistZ(p0, p1);
    }

    PLib::Point_nD<double,2> default_minDistZ_3(double p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,2>::minDistZ(p0, p1, p2);
    }

    PLib::Point_nD<double,2> default_minDistZ_4(double p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,2>::minDistZ(p0, p1, p2, p3);
    }

    PLib::Point_nD<double,2> default_minDistZ_5(double p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,2>::minDistZ(p0, p1, p2, p3, p4);
    }

    PLib::Point_nD<double,2> default_minDistZ_6(double p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,2>::minDistZ(p0, p1, p2, p3, p4, p5);
    }

    PLib::Point_nD<double,2> default_minDistZ_7(double p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,2>::minDistZ(p0, p1, p2, p3, p4, p5, p6);
    }

    PLib::Point_nD<double,2> default_minDistZ_8(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,2>::minDistZ(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    double extremum(int p0, CoordinateType p1, double p2, int p3, int p4, double p5, double p6) const {
        return call_method< double >(py_self, "extremum", p0, p1, p2, p3, p4, p5, p6);
    }

    double default_extremum_2(int p0, CoordinateType p1) const {
        return PLib::ParaCurve<double,2>::extremum(p0, p1);
    }

    double default_extremum_3(int p0, CoordinateType p1, double p2) const {
        return PLib::ParaCurve<double,2>::extremum(p0, p1, p2);
    }

    double default_extremum_4(int p0, CoordinateType p1, double p2, int p3) const {
        return PLib::ParaCurve<double,2>::extremum(p0, p1, p2, p3);
    }

    double default_extremum_5(int p0, CoordinateType p1, double p2, int p3, int p4) const {
        return PLib::ParaCurve<double,2>::extremum(p0, p1, p2, p3, p4);
    }

    double default_extremum_6(int p0, CoordinateType p1, double p2, int p3, int p4, double p5) const {
        return PLib::ParaCurve<double,2>::extremum(p0, p1, p2, p3, p4, p5);
    }

    double default_extremum_7(int p0, CoordinateType p1, double p2, int p3, int p4, double p5, double p6) const {
        return PLib::ParaCurve<double,2>::extremum(p0, p1, p2, p3, p4, p5, p6);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_basisFun_overloads_2_3, basisFun, 2, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_globalInterpD_overloads_4_5, globalInterpD, 4, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_projectTo_overloads_4_7, projectTo, 4, 7)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_length_overloads_0_2, length, 0, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_lengthIn_overloads_2_4, lengthIn, 2, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_writePS_overloads_1_5, writePS, 1, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_writePSp_overloads_3_7, writePSp, 3, 7)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_writeVRML_overloads_1_6, writeVRML, 1, 6)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_writeVRML97_overloads_1_6, writeVRML97, 1, 6)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_writeDisplayLINE_overloads_2_4, writeDisplayLINE, 2, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_drawImg_overloads_1_3, drawImg, 1, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_drawImg_overloads_2_3, drawImg, 2, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_drawAaImg_overloads_2_4, drawAaImg, 2, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_drawAaImg_overloads_3_5, drawAaImg, 3, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve2Dd_drawAaImg_overloads_4_6, drawAaImg, 4, 6)

struct NurbsCurve3Dd_Wrapper: PLib::NurbsCurve<double,3>
{
    NurbsCurve3Dd_Wrapper(PyObject* py_self_):
        PLib::NurbsCurve<double,3>(), py_self(py_self_) {}

    NurbsCurve3Dd_Wrapper(PyObject* py_self_, const PLib::NurbsCurve<double,3>& p0):
        PLib::NurbsCurve<double,3>(p0), py_self(py_self_) {}

    NurbsCurve3Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::HPoint_nD<double, 3> >& p0, const PLib::Vector<double>& p1):
        PLib::NurbsCurve<double,3>(p0, p1), py_self(py_self_) {}

    NurbsCurve3Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::HPoint_nD<double, 3> >& p0, const PLib::Vector<double>& p1, int p2):
        PLib::NurbsCurve<double,3>(p0, p1, p2), py_self(py_self_) {}

    NurbsCurve3Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::Point_nD<double, 3> >& p0, const PLib::Vector<double>& p1, const PLib::Vector<double>& p2):
        PLib::NurbsCurve<double,3>(p0, p1, p2), py_self(py_self_) {}

    NurbsCurve3Dd_Wrapper(PyObject* py_self_, const PLib::Vector<PLib::Point_nD<double, 3> >& p0, const PLib::Vector<double>& p1, const PLib::Vector<double>& p2, int p3):
        PLib::NurbsCurve<double,3>(p0, p1, p2, p3), py_self(py_self_) {}

    void reset(const PLib::Vector<PLib::HPoint_nD<double, 3> >& p0, const PLib::Vector<double>& p1, int p2) {
        call_method< void >(py_self, "reset", p0, p1, p2);
    }

    void default_reset(const PLib::Vector<PLib::HPoint_nD<double, 3> >& p0, const PLib::Vector<double>& p1, int p2) {
        PLib::NurbsCurve<double,3>::reset(p0, p1, p2);
    }

    PLib::HPoint_nD<double,3> hpointAt(double p0, int p1) const {
        return call_method< PLib::HPoint_nD<double,3> >(py_self, "hpointAt", p0, p1);
    }

    PLib::HPoint_nD<double,3> default_hpointAt(double p0, int p1) const {
        return PLib::NurbsCurve<double,3>::hpointAt(p0, p1);
    }

    void deriveAtH(double p0, int p1, PLib::Vector<PLib::HPoint_nD<double, 3> >& p2) const {
        call_method< void >(py_self, "deriveAtH", p0, p1, p2);
    }

    void default_deriveAtH(double p0, int p1, PLib::Vector<PLib::HPoint_nD<double, 3> >& p2) const {
        PLib::NurbsCurve<double,3>::deriveAtH(p0, p1, p2);
    }

    void deriveAt(double p0, int p1, PLib::Vector<PLib::Point_nD<double, 3> >& p2) const {
        call_method< void >(py_self, "deriveAt", p0, p1, p2);
    }

    void default_deriveAt(double p0, int p1, PLib::Vector<PLib::Point_nD<double, 3> >& p2) const {
        PLib::NurbsCurve<double,3>::deriveAt(p0, p1, p2);
    }

    double minKnot() const {
        return call_method< double >(py_self, "minKnot");
    }

    double default_minKnot() const {
        return PLib::NurbsCurve<double,3>::minKnot();
    }

    double maxKnot() const {
        return call_method< double >(py_self, "maxKnot");
    }

    double default_maxKnot() const {
        return PLib::NurbsCurve<double,3>::maxKnot();
    }

    void degreeElevate(int p0) {
        call_method< void >(py_self, "degreeElevate", p0);
    }

    void default_degreeElevate(int p0) {
        PLib::NurbsCurve<double,3>::degreeElevate(p0);
    }

    void modKnot(const PLib::Vector<double>& p0) {
        call_method< void >(py_self, "modKnot", p0);
    }

    void default_modKnot(const PLib::Vector<double>& p0) {
        PLib::NurbsCurve<double,3>::modKnot(p0);
    }

    int read(std::basic_ifstream<char,std::char_traits<char> >& p0) {
        return call_method< int >(py_self, "read", p0);
    }

    int default_read(std::basic_ifstream<char,std::char_traits<char> >& p0) {
        return PLib::NurbsCurve<double,3>::read(p0);
    }

    double minDist2(const PLib::Point_nD<double,3>& p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< double >(py_self, "minDist2", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    double default_minDist2_2(const PLib::Point_nD<double,3>& p0, double& p1) const {
        return PLib::ParaCurve<double,3>::minDist2(p0, p1);
    }

    double default_minDist2_3(const PLib::Point_nD<double,3>& p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,3>::minDist2(p0, p1, p2);
    }

    double default_minDist2_4(const PLib::Point_nD<double,3>& p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,3>::minDist2(p0, p1, p2, p3);
    }

    double default_minDist2_5(const PLib::Point_nD<double,3>& p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,3>::minDist2(p0, p1, p2, p3, p4);
    }

    double default_minDist2_6(const PLib::Point_nD<double,3>& p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,3>::minDist2(p0, p1, p2, p3, p4, p5);
    }

    double default_minDist2_7(const PLib::Point_nD<double,3>& p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,3>::minDist2(p0, p1, p2, p3, p4, p5, p6);
    }

    double default_minDist2_8(const PLib::Point_nD<double,3>& p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,3>::minDist2(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,3> minDistY(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< PLib::Point_nD<double,3> >(py_self, "minDistY", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,3> default_minDistY_2(double p0, double& p1) const {
        return PLib::ParaCurve<double,3>::minDistY(p0, p1);
    }

    PLib::Point_nD<double,3> default_minDistY_3(double p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,3>::minDistY(p0, p1, p2);
    }

    PLib::Point_nD<double,3> default_minDistY_4(double p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,3>::minDistY(p0, p1, p2, p3);
    }

    PLib::Point_nD<double,3> default_minDistY_5(double p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,3>::minDistY(p0, p1, p2, p3, p4);
    }

    PLib::Point_nD<double,3> default_minDistY_6(double p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,3>::minDistY(p0, p1, p2, p3, p4, p5);
    }

    PLib::Point_nD<double,3> default_minDistY_7(double p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,3>::minDistY(p0, p1, p2, p3, p4, p5, p6);
    }

    PLib::Point_nD<double,3> default_minDistY_8(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,3>::minDistY(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,3> minDistX(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< PLib::Point_nD<double,3> >(py_self, "minDistX", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,3> default_minDistX_2(double p0, double& p1) const {
        return PLib::ParaCurve<double,3>::minDistX(p0, p1);
    }

    PLib::Point_nD<double,3> default_minDistX_3(double p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,3>::minDistX(p0, p1, p2);
    }

    PLib::Point_nD<double,3> default_minDistX_4(double p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,3>::minDistX(p0, p1, p2, p3);
    }

    PLib::Point_nD<double,3> default_minDistX_5(double p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,3>::minDistX(p0, p1, p2, p3, p4);
    }

    PLib::Point_nD<double,3> default_minDistX_6(double p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,3>::minDistX(p0, p1, p2, p3, p4, p5);
    }

    PLib::Point_nD<double,3> default_minDistX_7(double p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,3>::minDistX(p0, p1, p2, p3, p4, p5, p6);
    }

    PLib::Point_nD<double,3> default_minDistX_8(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,3>::minDistX(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,3> minDistZ(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return call_method< PLib::Point_nD<double,3> >(py_self, "minDistZ", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    PLib::Point_nD<double,3> default_minDistZ_2(double p0, double& p1) const {
        return PLib::ParaCurve<double,3>::minDistZ(p0, p1);
    }

    PLib::Point_nD<double,3> default_minDistZ_3(double p0, double& p1, double p2) const {
        return PLib::ParaCurve<double,3>::minDistZ(p0, p1, p2);
    }

    PLib::Point_nD<double,3> default_minDistZ_4(double p0, double& p1, double p2, double p3) const {
        return PLib::ParaCurve<double,3>::minDistZ(p0, p1, p2, p3);
    }

    PLib::Point_nD<double,3> default_minDistZ_5(double p0, double& p1, double p2, double p3, int p4) const {
        return PLib::ParaCurve<double,3>::minDistZ(p0, p1, p2, p3, p4);
    }

    PLib::Point_nD<double,3> default_minDistZ_6(double p0, double& p1, double p2, double p3, int p4, int p5) const {
        return PLib::ParaCurve<double,3>::minDistZ(p0, p1, p2, p3, p4, p5);
    }

    PLib::Point_nD<double,3> default_minDistZ_7(double p0, double& p1, double p2, double p3, int p4, int p5, double p6) const {
        return PLib::ParaCurve<double,3>::minDistZ(p0, p1, p2, p3, p4, p5, p6);
    }

    PLib::Point_nD<double,3> default_minDistZ_8(double p0, double& p1, double p2, double p3, int p4, int p5, double p6, double p7) const {
        return PLib::ParaCurve<double,3>::minDistZ(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    double extremum(int p0, CoordinateType p1, double p2, int p3, int p4, double p5, double p6) const {
        return call_method< double >(py_self, "extremum", p0, p1, p2, p3, p4, p5, p6);
    }

    double default_extremum_2(int p0, CoordinateType p1) const {
        return PLib::ParaCurve<double,3>::extremum(p0, p1);
    }

    double default_extremum_3(int p0, CoordinateType p1, double p2) const {
        return PLib::ParaCurve<double,3>::extremum(p0, p1, p2);
    }

    double default_extremum_4(int p0, CoordinateType p1, double p2, int p3) const {
        return PLib::ParaCurve<double,3>::extremum(p0, p1, p2, p3);
    }

    double default_extremum_5(int p0, CoordinateType p1, double p2, int p3, int p4) const {
        return PLib::ParaCurve<double,3>::extremum(p0, p1, p2, p3, p4);
    }

    double default_extremum_6(int p0, CoordinateType p1, double p2, int p3, int p4, double p5) const {
        return PLib::ParaCurve<double,3>::extremum(p0, p1, p2, p3, p4, p5);
    }

    double default_extremum_7(int p0, CoordinateType p1, double p2, int p3, int p4, double p5, double p6) const {
        return PLib::ParaCurve<double,3>::extremum(p0, p1, p2, p3, p4, p5, p6);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_basisFun_overloads_2_3, basisFun, 2, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_globalInterpD_overloads_4_5, globalInterpD, 4, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_projectTo_overloads_4_7, projectTo, 4, 7)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_length_overloads_0_2, length, 0, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_lengthIn_overloads_2_4, lengthIn, 2, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_writePS_overloads_1_5, writePS, 1, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_writePSp_overloads_3_7, writePSp, 3, 7)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_writeVRML_overloads_1_6, writeVRML, 1, 6)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_writeVRML97_overloads_1_6, writeVRML97, 1, 6)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_writeDisplayLINE_overloads_2_4, writeDisplayLINE, 2, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_drawImg_overloads_1_3, drawImg, 1, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_drawImg_overloads_2_3, drawImg, 2, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_drawAaImg_overloads_2_4, drawAaImg, 2, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_drawAaImg_overloads_3_5, drawAaImg, 3, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsCurve3Dd_drawAaImg_overloads_4_6, drawAaImg, 4, 6)


}// namespace 


// Module ======================================================================
BOOST_PYTHON_MODULE(NurbsCurveD)
{
    class_< PLib::NurbsCurveArray<double,2>, NurbsCurveArray2Dd_Wrapper >("NurbsCurveArray2Dd", init<  >())
        .def(init< const PLib::NurbsCurveArray<double,2>& >())
        .def(init< PLib::NurbsCurve<double,2>*, int >())
        .def("resize", &PLib::NurbsCurveArray<double,2>::resize, &NurbsCurveArray2Dd_Wrapper::default_resize)
        .def("n", &PLib::NurbsCurveArray<double,2>::n)
        .def("init", &PLib::NurbsCurveArray<double,2>::init)
        .def("read", &PLib::NurbsCurveArray<double,2>::read)
        .def("write", &PLib::NurbsCurveArray<double,2>::write)
        .def("writePS", &PLib::NurbsCurveArray<double,2>::writePS, NurbsCurveArray2Dd_writePS_overloads_1_5())
        .def("writePSp", &PLib::NurbsCurveArray<double,2>::writePSp, NurbsCurveArray2Dd_writePSp_overloads_3_7())
    ;

    class_< PLib::NurbsCurveArray<double,3>, NurbsCurveArray3Dd_Wrapper >("NurbsCurveArray3Dd", init<  >())
        .def(init< const PLib::NurbsCurveArray<double,3>& >())
        .def(init< PLib::NurbsCurve<double,3>*, int >())
        .def("resize", &PLib::NurbsCurveArray<double,3>::resize, &NurbsCurveArray3Dd_Wrapper::default_resize)
        .def("n", &PLib::NurbsCurveArray<double,3>::n)
        .def("init", &PLib::NurbsCurveArray<double,3>::init)
        .def("read", &PLib::NurbsCurveArray<double,3>::read)
        .def("write", &PLib::NurbsCurveArray<double,3>::write)
        .def("writePS", &PLib::NurbsCurveArray<double,3>::writePS, NurbsCurveArray3Dd_writePS_overloads_1_5())
        .def("writePSp", &PLib::NurbsCurveArray<double,3>::writePSp, NurbsCurveArray3Dd_writePSp_overloads_3_7())
    ;

    class_< PLib::NurbsCurve<double,2>, NurbsCurve2Dd_Wrapper >("NurbsCurve2Dd", init<  >())
        .def(init< const PLib::NurbsCurve<double,2>& >())
        .def(init< const PLib::Vector<PLib::HPoint_nD<double, 2> >&, const PLib::Vector<double>&, optional< int > >())
        .def(init< const PLib::Vector<PLib::Point_nD<double, 2> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, optional< int > >())
        .def("reset", &PLib::NurbsCurve<double,2>::reset, &NurbsCurve2Dd_Wrapper::default_reset)
        .def("hpointAt", (PLib::HPoint_nD<double,2> (PLib::NurbsCurve<double,2>::*)(double, int) const)&PLib::NurbsCurve<double,2>::hpointAt, (PLib::HPoint_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, int) const)&NurbsCurve2Dd_Wrapper::default_hpointAt)
        .def("deriveAtH", (void (PLib::NurbsCurve<double,2>::*)(double, int, PLib::Vector<PLib::HPoint_nD<double, 2> >&) const)&PLib::NurbsCurve<double,2>::deriveAtH, (void (NurbsCurve2Dd_Wrapper::*)(double, int, PLib::Vector<PLib::HPoint_nD<double, 2> >&) const)&NurbsCurve2Dd_Wrapper::default_deriveAtH)
        .def("deriveAt", (void (PLib::NurbsCurve<double,2>::*)(double, int, PLib::Vector<PLib::Point_nD<double, 2> >&) const)&PLib::NurbsCurve<double,2>::deriveAt, (void (NurbsCurve2Dd_Wrapper::*)(double, int, PLib::Vector<PLib::Point_nD<double, 2> >&) const)&NurbsCurve2Dd_Wrapper::default_deriveAt)
        .def("minKnot", (double (PLib::NurbsCurve<double,2>::*)() const)&PLib::NurbsCurve<double,2>::minKnot, (double (NurbsCurve2Dd_Wrapper::*)() const)&NurbsCurve2Dd_Wrapper::default_minKnot)
        .def("maxKnot", (double (PLib::NurbsCurve<double,2>::*)() const)&PLib::NurbsCurve<double,2>::maxKnot, (double (NurbsCurve2Dd_Wrapper::*)() const)&NurbsCurve2Dd_Wrapper::default_maxKnot)
        .def("degreeElevate", &PLib::NurbsCurve<double,2>::degreeElevate, &NurbsCurve2Dd_Wrapper::default_degreeElevate)
        .def("modKnot", &PLib::NurbsCurve<double,2>::modKnot, &NurbsCurve2Dd_Wrapper::default_modKnot)
        .def("read", (int (PLib::NurbsCurve<double,2>::*)(std::basic_ifstream<char,std::char_traits<char> >&) )&PLib::NurbsCurve<double,2>::read, (int (NurbsCurve2Dd_Wrapper::*)(std::basic_ifstream<char,std::char_traits<char> >&))&NurbsCurve2Dd_Wrapper::default_read)
        .def("minDist2", (double (PLib::ParaCurve<double,2>::*)(const PLib::Point_nD<double,2>&, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,2>::minDist2, (double (NurbsCurve2Dd_Wrapper::*)(const PLib::Point_nD<double,2>&, double&, double, double, int, int, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDist2_8)
        .def("minDist2", (double (NurbsCurve2Dd_Wrapper::*)(const PLib::Point_nD<double,2>&, double&) const)&NurbsCurve2Dd_Wrapper::default_minDist2_2)
        .def("minDist2", (double (NurbsCurve2Dd_Wrapper::*)(const PLib::Point_nD<double,2>&, double&, double) const)&NurbsCurve2Dd_Wrapper::default_minDist2_3)
        .def("minDist2", (double (NurbsCurve2Dd_Wrapper::*)(const PLib::Point_nD<double,2>&, double&, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDist2_4)
        .def("minDist2", (double (NurbsCurve2Dd_Wrapper::*)(const PLib::Point_nD<double,2>&, double&, double, double, int) const)&NurbsCurve2Dd_Wrapper::default_minDist2_5)
        .def("minDist2", (double (NurbsCurve2Dd_Wrapper::*)(const PLib::Point_nD<double,2>&, double&, double, double, int, int) const)&NurbsCurve2Dd_Wrapper::default_minDist2_6)
        .def("minDist2", (double (NurbsCurve2Dd_Wrapper::*)(const PLib::Point_nD<double,2>&, double&, double, double, int, int, double) const)&NurbsCurve2Dd_Wrapper::default_minDist2_7)
        .def("minDistY", (PLib::Point_nD<double,2> (PLib::ParaCurve<double,2>::*)(double, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,2>::minDistY, (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDistY_8)
        .def("minDistY", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&) const)&NurbsCurve2Dd_Wrapper::default_minDistY_2)
        .def("minDistY", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double) const)&NurbsCurve2Dd_Wrapper::default_minDistY_3)
        .def("minDistY", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDistY_4)
        .def("minDistY", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int) const)&NurbsCurve2Dd_Wrapper::default_minDistY_5)
        .def("minDistY", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int) const)&NurbsCurve2Dd_Wrapper::default_minDistY_6)
        .def("minDistY", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int, double) const)&NurbsCurve2Dd_Wrapper::default_minDistY_7)
        .def("minDistX", (PLib::Point_nD<double,2> (PLib::ParaCurve<double,2>::*)(double, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,2>::minDistX, (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDistX_8)
        .def("minDistX", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&) const)&NurbsCurve2Dd_Wrapper::default_minDistX_2)
        .def("minDistX", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double) const)&NurbsCurve2Dd_Wrapper::default_minDistX_3)
        .def("minDistX", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDistX_4)
        .def("minDistX", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int) const)&NurbsCurve2Dd_Wrapper::default_minDistX_5)
        .def("minDistX", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int) const)&NurbsCurve2Dd_Wrapper::default_minDistX_6)
        .def("minDistX", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int, double) const)&NurbsCurve2Dd_Wrapper::default_minDistX_7)
        .def("minDistZ", (PLib::Point_nD<double,2> (PLib::ParaCurve<double,2>::*)(double, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,2>::minDistZ, (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDistZ_8)
        .def("minDistZ", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&) const)&NurbsCurve2Dd_Wrapper::default_minDistZ_2)
        .def("minDistZ", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double) const)&NurbsCurve2Dd_Wrapper::default_minDistZ_3)
        .def("minDistZ", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double) const)&NurbsCurve2Dd_Wrapper::default_minDistZ_4)
        .def("minDistZ", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int) const)&NurbsCurve2Dd_Wrapper::default_minDistZ_5)
        .def("minDistZ", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int) const)&NurbsCurve2Dd_Wrapper::default_minDistZ_6)
        .def("minDistZ", (PLib::Point_nD<double,2> (NurbsCurve2Dd_Wrapper::*)(double, double&, double, double, int, int, double) const)&NurbsCurve2Dd_Wrapper::default_minDistZ_7)
        .def("extremum", (double (PLib::ParaCurve<double,2>::*)(int, CoordinateType, double, int, int, double, double) const)&PLib::ParaCurve<double,2>::extremum, (double (NurbsCurve2Dd_Wrapper::*)(int, CoordinateType, double, int, int, double, double) const)&NurbsCurve2Dd_Wrapper::default_extremum_7)
        .def("extremum", (double (NurbsCurve2Dd_Wrapper::*)(int, CoordinateType) const)&NurbsCurve2Dd_Wrapper::default_extremum_2)
        .def("extremum", (double (NurbsCurve2Dd_Wrapper::*)(int, CoordinateType, double) const)&NurbsCurve2Dd_Wrapper::default_extremum_3)
        .def("extremum", (double (NurbsCurve2Dd_Wrapper::*)(int, CoordinateType, double, int) const)&NurbsCurve2Dd_Wrapper::default_extremum_4)
        .def("extremum", (double (NurbsCurve2Dd_Wrapper::*)(int, CoordinateType, double, int, int) const)&NurbsCurve2Dd_Wrapper::default_extremum_5)
        .def("extremum", (double (NurbsCurve2Dd_Wrapper::*)(int, CoordinateType, double, int, int, double) const)&NurbsCurve2Dd_Wrapper::default_extremum_6)
        .def("degree", &PLib::NurbsCurve<double,2>::degree)
        .def("ctrlPnts", (const PLib::Vector<PLib::HPoint_nD<double, 2> >& (PLib::NurbsCurve<double,2>::*)() const)&PLib::NurbsCurve<double,2>::ctrlPnts, return_value_policy< copy_const_reference >())
        .def("ctrlPnts", (const PLib::HPoint_nD<double,2> (PLib::NurbsCurve<double,2>::*)(int) const)&PLib::NurbsCurve<double,2>::ctrlPnts)
        .def("knot", (const PLib::Vector<double>& (PLib::NurbsCurve<double,2>::*)() const)&PLib::NurbsCurve<double,2>::knot, return_value_policy< copy_const_reference >())
        .def("knot", (double (PLib::NurbsCurve<double,2>::*)(int) const)&PLib::NurbsCurve<double,2>::knot)
        .def("resize", &PLib::NurbsCurve<double,2>::resize)
        .def("hpointAt", (PLib::HPoint_nD<double,2> (PLib::NurbsCurve<double,2>::*)(double) const)&PLib::NurbsCurve<double,2>::hpointAt)
        .def("deriveAtH", (void (PLib::NurbsCurve<double,2>::*)(double, int, int, PLib::Vector<PLib::HPoint_nD<double, 2> >&) const)&PLib::NurbsCurve<double,2>::deriveAtH)
        .def("deriveAt", (void (PLib::NurbsCurve<double,2>::*)(double, int, int, PLib::Vector<PLib::Point_nD<double, 2> >&) const)&PLib::NurbsCurve<double,2>::deriveAt)
        .def("derive3D", &PLib::NurbsCurve<double,2>::derive3D)
        .def("derive", &PLib::NurbsCurve<double,2>::derive)
        .def("normal", &PLib::NurbsCurve<double,2>::normal)
        .def("firstD", (PLib::HPoint_nD<double,2> (PLib::NurbsCurve<double,2>::*)(double) const)&PLib::NurbsCurve<double,2>::firstD)
        .def("firstD", (PLib::HPoint_nD<double,2> (PLib::NurbsCurve<double,2>::*)(double, int) const)&PLib::NurbsCurve<double,2>::firstD)
        .def("firstDn", (PLib::Point_nD<double,2> (PLib::NurbsCurve<double,2>::*)(double) const)&PLib::NurbsCurve<double,2>::firstDn)
        .def("firstDn", (PLib::Point_nD<double,2> (PLib::NurbsCurve<double,2>::*)(double, int) const)&PLib::NurbsCurve<double,2>::firstDn)
        .def("basisFun", &PLib::NurbsCurve<double,2>::basisFun, NurbsCurve2Dd_basisFun_overloads_2_3())
        .def("basisFuns", &PLib::NurbsCurve<double,2>::basisFuns)
        .def("dersBasisFuns", &PLib::NurbsCurve<double,2>::dersBasisFuns)
        .def("findSpan", &PLib::NurbsCurve<double,2>::findSpan)
        .def("findMultSpan", &PLib::NurbsCurve<double,2>::findMultSpan)
        .def("findMult", &PLib::NurbsCurve<double,2>::findMult)
        .def("findKnot", &PLib::NurbsCurve<double,2>::findKnot)
        .def("getRemovalBnd", &PLib::NurbsCurve<double,2>::getRemovalBnd)
        .def("removeKnot", &PLib::NurbsCurve<double,2>::removeKnot)
        .def("removeKnotsBound", &PLib::NurbsCurve<double,2>::removeKnotsBound)
        .def("knotInsertion", &PLib::NurbsCurve<double,2>::knotInsertion)
        .def("refineKnotVector", &PLib::NurbsCurve<double,2>::refineKnotVector)
        .def("refineKnotVectorClosed", &PLib::NurbsCurve<double,2>::refineKnotVectorClosed)
        .def("mergeKnotVector", &PLib::NurbsCurve<double,2>::mergeKnotVector)
        .def("clamp", &PLib::NurbsCurve<double,2>::clamp)
        .def("unclamp", &PLib::NurbsCurve<double,2>::unclamp)
        .def("leastSquares", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int, int) )&PLib::NurbsCurve<double,2>::leastSquares)
        .def("leastSquares", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquares)
        .def("leastSquaresH", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquaresH)
        .def("leastSquares", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquares)
        .def("leastSquaresH", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquaresH)
        .def("leastSquaresClosed", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int, int) )&PLib::NurbsCurve<double,2>::leastSquaresClosed)
        .def("leastSquaresClosed", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquaresClosed)
        .def("leastSquaresClosedH", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquaresClosedH)
        .def("leastSquaresClosed", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquaresClosed)
        .def("leastSquaresClosedH", (int (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,2>::leastSquaresClosedH)
        .def("globalApproxErrBnd", (void (PLib::NurbsCurve<double,2>::*)(PLib::Vector<PLib::Point_nD<double, 2> >&, int, double) )&PLib::NurbsCurve<double,2>::globalApproxErrBnd)
        .def("globalApproxErrBnd", (void (PLib::NurbsCurve<double,2>::*)(PLib::Vector<PLib::Point_nD<double, 2> >&, PLib::Vector<double>&, int, double) )&PLib::NurbsCurve<double,2>::globalApproxErrBnd)
        .def("globalApproxErrBnd2", &PLib::NurbsCurve<double,2>::globalApproxErrBnd2)
        .def("globalApproxErrBnd3", (void (PLib::NurbsCurve<double,2>::*)(PLib::Vector<PLib::Point_nD<double, 2> >&, int, double) )&PLib::NurbsCurve<double,2>::globalApproxErrBnd3)
        .def("globalApproxErrBnd3", (void (PLib::NurbsCurve<double,2>::*)(PLib::Vector<PLib::Point_nD<double, 2> >&, const PLib::Vector<double>&, int, double) )&PLib::NurbsCurve<double,2>::globalApproxErrBnd3)
        .def("globalInterp", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int) )&PLib::NurbsCurve<double,2>::globalInterp)
        .def("globalInterp", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,2>::globalInterp)
        .def("globalInterpH", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, int) )&PLib::NurbsCurve<double,2>::globalInterpH)
        .def("globalInterpH", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,2>::globalInterpH)
        .def("globalInterpH", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,2>::globalInterpH)
        .def("globalInterpClosed", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, int) )&PLib::NurbsCurve<double,2>::globalInterpClosed)
        .def("globalInterpClosed", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,2>::globalInterpClosed)
        .def("globalInterpClosedH", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, int) )&PLib::NurbsCurve<double,2>::globalInterpClosedH)
        .def("globalInterpClosedH", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,2>::globalInterpClosedH)
        .def("globalInterpClosedH", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::HPoint_nD<double, 2> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,2>::globalInterpClosedH)
        .def("globalInterpClosed", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Vector<PLib::Point_nD<double, 2> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,2>::globalInterpClosed)
        .def("globalInterpD", &PLib::NurbsCurve<double,2>::globalInterpD, NurbsCurve2Dd_globalInterpD_overloads_4_5())
        .def("projectTo", &PLib::NurbsCurve<double,2>::projectTo, NurbsCurve2Dd_projectTo_overloads_4_7())
        .def("length", &PLib::NurbsCurve<double,2>::length, NurbsCurve2Dd_length_overloads_0_2())
        .def("lengthIn", &PLib::NurbsCurve<double,2>::lengthIn, NurbsCurve2Dd_lengthIn_overloads_2_4())
        .def("lengthF", (double (PLib::NurbsCurve<double,2>::*)(double) const)&PLib::NurbsCurve<double,2>::lengthF)
        .def("lengthF", (double (PLib::NurbsCurve<double,2>::*)(double, int) const)&PLib::NurbsCurve<double,2>::lengthF)
        .def("makeCircle", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Point_nD<double,2>&, const PLib::Point_nD<double,2>&, const PLib::Point_nD<double,2>&, double, double, double) )&PLib::NurbsCurve<double,2>::makeCircle)
        .def("makeCircle", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Point_nD<double,2>&, double, double, double) )&PLib::NurbsCurve<double,2>::makeCircle)
        .def("makeCircle", (void (PLib::NurbsCurve<double,2>::*)(const PLib::Point_nD<double,2>&, double) )&PLib::NurbsCurve<double,2>::makeCircle)
        .def("makeLine", &PLib::NurbsCurve<double,2>::makeLine)
        .def("decompose", &PLib::NurbsCurve<double,2>::decompose)
        .def("decomposeClosed", &PLib::NurbsCurve<double,2>::decomposeClosed)
        .def("splitAt", &PLib::NurbsCurve<double,2>::splitAt)
        .def("mergeOf", &PLib::NurbsCurve<double,2>::mergeOf)
        .def("transform", &PLib::NurbsCurve<double,2>::transform)
        .def("modCP", &PLib::NurbsCurve<double,2>::modCP)
        .def("modCPby", &PLib::NurbsCurve<double,2>::modCPby)
        .def("movePoint", (int (PLib::NurbsCurve<double,2>::*)(double, const PLib::Point_nD<double,2>&) )&PLib::NurbsCurve<double,2>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,2>::*)(double, const PLib::BasicArray<PLib::Point_nD<double, 2> >&) )&PLib::NurbsCurve<double,2>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,2>::*)(const PLib::BasicArray<double>&, const PLib::BasicArray<PLib::Point_nD<double, 2> >&) )&PLib::NurbsCurve<double,2>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,2>::*)(const PLib::BasicArray<double>&, const PLib::BasicArray<PLib::Point_nD<double, 2> >&, const PLib::BasicArray<int>&, const PLib::BasicArray<int>&) )&PLib::NurbsCurve<double,2>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,2>::*)(const PLib::BasicArray<double>&, const PLib::BasicArray<PLib::Point_nD<double, 2> >&, const PLib::BasicArray<int>&, const PLib::BasicArray<int>&, const PLib::BasicArray<int>&) )&PLib::NurbsCurve<double,2>::movePoint)
        .def("setTangent", &PLib::NurbsCurve<double,2>::setTangent)
        .def("setTangentAtEnd", &PLib::NurbsCurve<double,2>::setTangentAtEnd)
        .def("read", (int (PLib::NurbsCurve<double,2>::*)(const char*) )&PLib::NurbsCurve<double,2>::read)
        .def("write", (int (PLib::NurbsCurve<double,2>::*)(const char*) const)&PLib::NurbsCurve<double,2>::write)
        .def("write", (int (PLib::NurbsCurve<double,2>::*)(std::basic_ofstream<char,std::char_traits<char> >&) const)&PLib::NurbsCurve<double,2>::write)
        .def("writePS", &PLib::NurbsCurve<double,2>::writePS, NurbsCurve2Dd_writePS_overloads_1_5())
        .def("writePSp", &PLib::NurbsCurve<double,2>::writePSp, NurbsCurve2Dd_writePSp_overloads_3_7())
//         .def("writeVRML", (int (PLib::NurbsCurve<double,2>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,2>::writeVRML)
        .def("writeVRML", (int (PLib::NurbsCurve<double,2>::*)(const char*, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,2>::writeVRML)
        .def("writeVRML", (int (PLib::NurbsCurve<double,2>::*)(const char*, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,2>::writeVRML, NurbsCurve2Dd_writeVRML_overloads_1_6())
//         .def("writeVRML", (int (PLib::NurbsCurve<double,2>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,2>::writeVRML, NurbsCurve2Dd_writeVRML_overloads_1_6())
        .def("writeVRML97", (int (PLib::NurbsCurve<double,2>::*)(const char*, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,2>::writeVRML97)
//         .def("writeVRML97", (int (PLib::NurbsCurve<double,2>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,2>::writeVRML97)
        .def("writeVRML97", (int (PLib::NurbsCurve<double,2>::*)(const char*, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,2>::writeVRML97, NurbsCurve2Dd_writeVRML97_overloads_1_6())
//         .def("writeVRML97", (int (PLib::NurbsCurve<double,2>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,2>::writeVRML97, NurbsCurve2Dd_writeVRML97_overloads_1_6())
        .def("writeDisplayLINE", (int (PLib::NurbsCurve<double,2>::*)(const char*, int, const PLib::Color&, double) const)&PLib::NurbsCurve<double,2>::writeDisplayLINE, NurbsCurve2Dd_writeDisplayLINE_overloads_2_4())
        .def("writeDisplayLINE", (int (PLib::NurbsCurve<double,2>::*)(const char*, const PLib::Color&, int, double, double) const)&PLib::NurbsCurve<double,2>::writeDisplayLINE)
        .def("drawImg", (void (PLib::NurbsCurve<double,2>::*)(PLib::MatrixImage<unsigned char>&, unsigned char, double) )&PLib::NurbsCurve<double,2>::drawImg, NurbsCurve2Dd_drawImg_overloads_1_3())
        .def("drawImg", (void (PLib::NurbsCurve<double,2>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, double) )&PLib::NurbsCurve<double,2>::drawImg, NurbsCurve2Dd_drawImg_overloads_2_3())
        .def("drawAaImg", (void (PLib::NurbsCurve<double,2>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, int, int) )&PLib::NurbsCurve<double,2>::drawAaImg, NurbsCurve2Dd_drawAaImg_overloads_2_4())
        .def("drawAaImg", (void (PLib::NurbsCurve<double,2>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, const PLib::NurbsCurve<double,3>&, int, int) )&PLib::NurbsCurve<double,2>::drawAaImg, NurbsCurve2Dd_drawAaImg_overloads_3_5())
        .def("drawAaImg", (PLib::NurbsSurface<double,3> (PLib::NurbsCurve<double,2>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, const PLib::NurbsCurve<double,3>&, const PLib::NurbsCurve<double,3>&, int, int) )&PLib::NurbsCurve<double,2>::drawAaImg, NurbsCurve2Dd_drawAaImg_overloads_4_6())
        .def("tesselate", &PLib::NurbsCurve<double,2>::tesselate)
        .def("pointAt", (PLib::Point_nD<double,2> (PLib::ParaCurve<double,2>::*)(double) const)&PLib::ParaCurve<double,2>::pointAt)
        .def("pointAt", (PLib::Point_nD<double,2> (PLib::ParaCurve<double,2>::*)(double, int) )&PLib::ParaCurve<double,2>::pointAt)
        .def("__call__", &PLib::NurbsCurve<double,2>::operator ())
    ;

    class_< PLib::NurbsCurve<double,3>, NurbsCurve3Dd_Wrapper >("NurbsCurve3Dd", init<  >())
        .def(init< const PLib::NurbsCurve<double,3>& >())
        .def(init< const PLib::Vector<PLib::HPoint_nD<double, 3> >&, const PLib::Vector<double>&, optional< int > >())
        .def(init< const PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, optional< int > >())
        .def("reset", &PLib::NurbsCurve<double,3>::reset, &NurbsCurve3Dd_Wrapper::default_reset)
        .def("hpointAt", (PLib::HPoint_nD<double,3> (PLib::NurbsCurve<double,3>::*)(double, int) const)&PLib::NurbsCurve<double,3>::hpointAt, (PLib::HPoint_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, int) const)&NurbsCurve3Dd_Wrapper::default_hpointAt)
        .def("deriveAtH", (void (PLib::NurbsCurve<double,3>::*)(double, int, PLib::Vector<PLib::HPoint_nD<double, 3> >&) const)&PLib::NurbsCurve<double,3>::deriveAtH, (void (NurbsCurve3Dd_Wrapper::*)(double, int, PLib::Vector<PLib::HPoint_nD<double, 3> >&) const)&NurbsCurve3Dd_Wrapper::default_deriveAtH)
        .def("deriveAt", (void (PLib::NurbsCurve<double,3>::*)(double, int, PLib::Vector<PLib::Point_nD<double, 3> >&) const)&PLib::NurbsCurve<double,3>::deriveAt, (void (NurbsCurve3Dd_Wrapper::*)(double, int, PLib::Vector<PLib::Point_nD<double, 3> >&) const)&NurbsCurve3Dd_Wrapper::default_deriveAt)
        .def("minKnot", (double (PLib::NurbsCurve<double,3>::*)() const)&PLib::NurbsCurve<double,3>::minKnot, (double (NurbsCurve3Dd_Wrapper::*)() const)&NurbsCurve3Dd_Wrapper::default_minKnot)
        .def("maxKnot", (double (PLib::NurbsCurve<double,3>::*)() const)&PLib::NurbsCurve<double,3>::maxKnot, (double (NurbsCurve3Dd_Wrapper::*)() const)&NurbsCurve3Dd_Wrapper::default_maxKnot)
        .def("degreeElevate", &PLib::NurbsCurve<double,3>::degreeElevate, &NurbsCurve3Dd_Wrapper::default_degreeElevate)
        .def("modKnot", &PLib::NurbsCurve<double,3>::modKnot, &NurbsCurve3Dd_Wrapper::default_modKnot)
        .def("read", (int (PLib::NurbsCurve<double,3>::*)(std::basic_ifstream<char,std::char_traits<char> >&) )&PLib::NurbsCurve<double,3>::read, (int (NurbsCurve3Dd_Wrapper::*)(std::basic_ifstream<char,std::char_traits<char> >&))&NurbsCurve3Dd_Wrapper::default_read)
        .def("minDist2", (double (PLib::ParaCurve<double,3>::*)(const PLib::Point_nD<double,3>&, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,3>::minDist2, (double (NurbsCurve3Dd_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double, double, int, int, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDist2_8)
        .def("minDist2", (double (NurbsCurve3Dd_Wrapper::*)(const PLib::Point_nD<double,3>&, double&) const)&NurbsCurve3Dd_Wrapper::default_minDist2_2)
        .def("minDist2", (double (NurbsCurve3Dd_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double) const)&NurbsCurve3Dd_Wrapper::default_minDist2_3)
        .def("minDist2", (double (NurbsCurve3Dd_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDist2_4)
        .def("minDist2", (double (NurbsCurve3Dd_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double, double, int) const)&NurbsCurve3Dd_Wrapper::default_minDist2_5)
        .def("minDist2", (double (NurbsCurve3Dd_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double, double, int, int) const)&NurbsCurve3Dd_Wrapper::default_minDist2_6)
        .def("minDist2", (double (NurbsCurve3Dd_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double, double, int, int, double) const)&NurbsCurve3Dd_Wrapper::default_minDist2_7)
        .def("minDistY", (PLib::Point_nD<double,3> (PLib::ParaCurve<double,3>::*)(double, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,3>::minDistY, (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDistY_8)
        .def("minDistY", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&) const)&NurbsCurve3Dd_Wrapper::default_minDistY_2)
        .def("minDistY", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double) const)&NurbsCurve3Dd_Wrapper::default_minDistY_3)
        .def("minDistY", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDistY_4)
        .def("minDistY", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int) const)&NurbsCurve3Dd_Wrapper::default_minDistY_5)
        .def("minDistY", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int) const)&NurbsCurve3Dd_Wrapper::default_minDistY_6)
        .def("minDistY", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int, double) const)&NurbsCurve3Dd_Wrapper::default_minDistY_7)
        .def("minDistX", (PLib::Point_nD<double,3> (PLib::ParaCurve<double,3>::*)(double, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,3>::minDistX, (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDistX_8)
        .def("minDistX", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&) const)&NurbsCurve3Dd_Wrapper::default_minDistX_2)
        .def("minDistX", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double) const)&NurbsCurve3Dd_Wrapper::default_minDistX_3)
        .def("minDistX", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDistX_4)
        .def("minDistX", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int) const)&NurbsCurve3Dd_Wrapper::default_minDistX_5)
        .def("minDistX", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int) const)&NurbsCurve3Dd_Wrapper::default_minDistX_6)
        .def("minDistX", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int, double) const)&NurbsCurve3Dd_Wrapper::default_minDistX_7)
        .def("minDistZ", (PLib::Point_nD<double,3> (PLib::ParaCurve<double,3>::*)(double, double&, double, double, int, int, double, double) const)&PLib::ParaCurve<double,3>::minDistZ, (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDistZ_8)
        .def("minDistZ", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&) const)&NurbsCurve3Dd_Wrapper::default_minDistZ_2)
        .def("minDistZ", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double) const)&NurbsCurve3Dd_Wrapper::default_minDistZ_3)
        .def("minDistZ", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double) const)&NurbsCurve3Dd_Wrapper::default_minDistZ_4)
        .def("minDistZ", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int) const)&NurbsCurve3Dd_Wrapper::default_minDistZ_5)
        .def("minDistZ", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int) const)&NurbsCurve3Dd_Wrapper::default_minDistZ_6)
        .def("minDistZ", (PLib::Point_nD<double,3> (NurbsCurve3Dd_Wrapper::*)(double, double&, double, double, int, int, double) const)&NurbsCurve3Dd_Wrapper::default_minDistZ_7)
        .def("extremum", (double (PLib::ParaCurve<double,3>::*)(int, CoordinateType, double, int, int, double, double) const)&PLib::ParaCurve<double,3>::extremum, (double (NurbsCurve3Dd_Wrapper::*)(int, CoordinateType, double, int, int, double, double) const)&NurbsCurve3Dd_Wrapper::default_extremum_7)
        .def("extremum", (double (NurbsCurve3Dd_Wrapper::*)(int, CoordinateType) const)&NurbsCurve3Dd_Wrapper::default_extremum_2)
        .def("extremum", (double (NurbsCurve3Dd_Wrapper::*)(int, CoordinateType, double) const)&NurbsCurve3Dd_Wrapper::default_extremum_3)
        .def("extremum", (double (NurbsCurve3Dd_Wrapper::*)(int, CoordinateType, double, int) const)&NurbsCurve3Dd_Wrapper::default_extremum_4)
        .def("extremum", (double (NurbsCurve3Dd_Wrapper::*)(int, CoordinateType, double, int, int) const)&NurbsCurve3Dd_Wrapper::default_extremum_5)
        .def("extremum", (double (NurbsCurve3Dd_Wrapper::*)(int, CoordinateType, double, int, int, double) const)&NurbsCurve3Dd_Wrapper::default_extremum_6)
        .def("degree", &PLib::NurbsCurve<double,3>::degree)
        .def("ctrlPnts", (const PLib::Vector<PLib::HPoint_nD<double, 3> >& (PLib::NurbsCurve<double,3>::*)() const)&PLib::NurbsCurve<double,3>::ctrlPnts, return_value_policy< copy_const_reference >())
        .def("ctrlPnts", (const PLib::HPoint_nD<double,3> (PLib::NurbsCurve<double,3>::*)(int) const)&PLib::NurbsCurve<double,3>::ctrlPnts)
        .def("knot", (const PLib::Vector<double>& (PLib::NurbsCurve<double,3>::*)() const)&PLib::NurbsCurve<double,3>::knot, return_value_policy< copy_const_reference >())
        .def("knot", (double (PLib::NurbsCurve<double,3>::*)(int) const)&PLib::NurbsCurve<double,3>::knot)
        .def("resize", &PLib::NurbsCurve<double,3>::resize)
        .def("hpointAt", (PLib::HPoint_nD<double,3> (PLib::NurbsCurve<double,3>::*)(double) const)&PLib::NurbsCurve<double,3>::hpointAt)
        .def("deriveAtH", (void (PLib::NurbsCurve<double,3>::*)(double, int, int, PLib::Vector<PLib::HPoint_nD<double, 3> >&) const)&PLib::NurbsCurve<double,3>::deriveAtH)
        .def("deriveAt", (void (PLib::NurbsCurve<double,3>::*)(double, int, int, PLib::Vector<PLib::Point_nD<double, 3> >&) const)&PLib::NurbsCurve<double,3>::deriveAt)
        .def("derive3D", &PLib::NurbsCurve<double,3>::derive3D)
        .def("derive", &PLib::NurbsCurve<double,3>::derive)
        .def("normal", &PLib::NurbsCurve<double,3>::normal)
        .def("firstD", (PLib::HPoint_nD<double,3> (PLib::NurbsCurve<double,3>::*)(double) const)&PLib::NurbsCurve<double,3>::firstD)
        .def("firstD", (PLib::HPoint_nD<double,3> (PLib::NurbsCurve<double,3>::*)(double, int) const)&PLib::NurbsCurve<double,3>::firstD)
        .def("firstDn", (PLib::Point_nD<double,3> (PLib::NurbsCurve<double,3>::*)(double) const)&PLib::NurbsCurve<double,3>::firstDn)
        .def("firstDn", (PLib::Point_nD<double,3> (PLib::NurbsCurve<double,3>::*)(double, int) const)&PLib::NurbsCurve<double,3>::firstDn)
        .def("basisFun", &PLib::NurbsCurve<double,3>::basisFun, NurbsCurve3Dd_basisFun_overloads_2_3())
        .def("basisFuns", &PLib::NurbsCurve<double,3>::basisFuns)
        .def("dersBasisFuns", &PLib::NurbsCurve<double,3>::dersBasisFuns)
        .def("findSpan", &PLib::NurbsCurve<double,3>::findSpan)
        .def("findMultSpan", &PLib::NurbsCurve<double,3>::findMultSpan)
        .def("findMult", &PLib::NurbsCurve<double,3>::findMult)
        .def("findKnot", &PLib::NurbsCurve<double,3>::findKnot)
        .def("getRemovalBnd", &PLib::NurbsCurve<double,3>::getRemovalBnd)
        .def("removeKnot", &PLib::NurbsCurve<double,3>::removeKnot)
        .def("removeKnotsBound", &PLib::NurbsCurve<double,3>::removeKnotsBound)
        .def("knotInsertion", &PLib::NurbsCurve<double,3>::knotInsertion)
        .def("refineKnotVector", &PLib::NurbsCurve<double,3>::refineKnotVector)
        .def("refineKnotVectorClosed", &PLib::NurbsCurve<double,3>::refineKnotVectorClosed)
        .def("mergeKnotVector", &PLib::NurbsCurve<double,3>::mergeKnotVector)
        .def("clamp", &PLib::NurbsCurve<double,3>::clamp)
        .def("unclamp", &PLib::NurbsCurve<double,3>::unclamp)
        .def("leastSquares", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int, int) )&PLib::NurbsCurve<double,3>::leastSquares)
        .def("leastSquares", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquares)
        .def("leastSquaresH", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquaresH)
        .def("leastSquares", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquares)
        .def("leastSquaresH", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquaresH)
        .def("leastSquaresClosed", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int, int) )&PLib::NurbsCurve<double,3>::leastSquaresClosed)
        .def("leastSquaresClosed", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquaresClosed)
        .def("leastSquaresClosedH", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, int, int, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquaresClosedH)
        .def("leastSquaresClosed", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquaresClosed)
        .def("leastSquaresClosedH", (int (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, int, int, const PLib::Vector<double>&, const PLib::Vector<double>&) )&PLib::NurbsCurve<double,3>::leastSquaresClosedH)
        .def("globalApproxErrBnd", (void (PLib::NurbsCurve<double,3>::*)(PLib::Vector<PLib::Point_nD<double, 3> >&, int, double) )&PLib::NurbsCurve<double,3>::globalApproxErrBnd)
        .def("globalApproxErrBnd", (void (PLib::NurbsCurve<double,3>::*)(PLib::Vector<PLib::Point_nD<double, 3> >&, PLib::Vector<double>&, int, double) )&PLib::NurbsCurve<double,3>::globalApproxErrBnd)
        .def("globalApproxErrBnd2", &PLib::NurbsCurve<double,3>::globalApproxErrBnd2)
        .def("globalApproxErrBnd3", (void (PLib::NurbsCurve<double,3>::*)(PLib::Vector<PLib::Point_nD<double, 3> >&, int, double) )&PLib::NurbsCurve<double,3>::globalApproxErrBnd3)
        .def("globalApproxErrBnd3", (void (PLib::NurbsCurve<double,3>::*)(PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<double>&, int, double) )&PLib::NurbsCurve<double,3>::globalApproxErrBnd3)
        .def("globalInterp", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int) )&PLib::NurbsCurve<double,3>::globalInterp)
        .def("globalInterp", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,3>::globalInterp)
        .def("globalInterpH", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, int) )&PLib::NurbsCurve<double,3>::globalInterpH)
        .def("globalInterpH", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,3>::globalInterpH)
        .def("globalInterpH", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,3>::globalInterpH)
        .def("globalInterpClosed", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, int) )&PLib::NurbsCurve<double,3>::globalInterpClosed)
        .def("globalInterpClosed", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,3>::globalInterpClosed)
        .def("globalInterpClosedH", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, int) )&PLib::NurbsCurve<double,3>::globalInterpClosedH)
        .def("globalInterpClosedH", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,3>::globalInterpClosedH)
        .def("globalInterpClosedH", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::HPoint_nD<double, 3> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,3>::globalInterpClosedH)
        .def("globalInterpClosed", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<double>&, const PLib::Vector<double>&, int) )&PLib::NurbsCurve<double,3>::globalInterpClosed)
        .def("globalInterpD", &PLib::NurbsCurve<double,3>::globalInterpD, NurbsCurve3Dd_globalInterpD_overloads_4_5())
        .def("projectTo", &PLib::NurbsCurve<double,3>::projectTo, NurbsCurve3Dd_projectTo_overloads_4_7())
        .def("length", &PLib::NurbsCurve<double,3>::length, NurbsCurve3Dd_length_overloads_0_2())
        .def("lengthIn", &PLib::NurbsCurve<double,3>::lengthIn, NurbsCurve3Dd_lengthIn_overloads_2_4())
        .def("lengthF", (double (PLib::NurbsCurve<double,3>::*)(double) const)&PLib::NurbsCurve<double,3>::lengthF)
        .def("lengthF", (double (PLib::NurbsCurve<double,3>::*)(double, int) const)&PLib::NurbsCurve<double,3>::lengthF)
        .def("makeCircle", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Point_nD<double,3>&, const PLib::Point_nD<double,3>&, const PLib::Point_nD<double,3>&, double, double, double) )&PLib::NurbsCurve<double,3>::makeCircle)
        .def("makeCircle", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Point_nD<double,3>&, double, double, double) )&PLib::NurbsCurve<double,3>::makeCircle)
        .def("makeCircle", (void (PLib::NurbsCurve<double,3>::*)(const PLib::Point_nD<double,3>&, double) )&PLib::NurbsCurve<double,3>::makeCircle)
        .def("makeLine", &PLib::NurbsCurve<double,3>::makeLine)
        .def("decompose", &PLib::NurbsCurve<double,3>::decompose)
        .def("decomposeClosed", &PLib::NurbsCurve<double,3>::decomposeClosed)
        .def("splitAt", &PLib::NurbsCurve<double,3>::splitAt)
        .def("mergeOf", &PLib::NurbsCurve<double,3>::mergeOf)
        .def("transform", &PLib::NurbsCurve<double,3>::transform)
        .def("modCP", &PLib::NurbsCurve<double,3>::modCP)
        .def("modCPby", &PLib::NurbsCurve<double,3>::modCPby)
        .def("movePoint", (int (PLib::NurbsCurve<double,3>::*)(double, const PLib::Point_nD<double,3>&) )&PLib::NurbsCurve<double,3>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,3>::*)(double, const PLib::BasicArray<PLib::Point_nD<double, 3> >&) )&PLib::NurbsCurve<double,3>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,3>::*)(const PLib::BasicArray<double>&, const PLib::BasicArray<PLib::Point_nD<double, 3> >&) )&PLib::NurbsCurve<double,3>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,3>::*)(const PLib::BasicArray<double>&, const PLib::BasicArray<PLib::Point_nD<double, 3> >&, const PLib::BasicArray<int>&, const PLib::BasicArray<int>&) )&PLib::NurbsCurve<double,3>::movePoint)
        .def("movePoint", (int (PLib::NurbsCurve<double,3>::*)(const PLib::BasicArray<double>&, const PLib::BasicArray<PLib::Point_nD<double, 3> >&, const PLib::BasicArray<int>&, const PLib::BasicArray<int>&, const PLib::BasicArray<int>&) )&PLib::NurbsCurve<double,3>::movePoint)
        .def("setTangent", &PLib::NurbsCurve<double,3>::setTangent)
        .def("setTangentAtEnd", &PLib::NurbsCurve<double,3>::setTangentAtEnd)
        .def("read", (int (PLib::NurbsCurve<double,3>::*)(const char*) )&PLib::NurbsCurve<double,3>::read)
        .def("write", (int (PLib::NurbsCurve<double,3>::*)(const char*) const)&PLib::NurbsCurve<double,3>::write)
        .def("write", (int (PLib::NurbsCurve<double,3>::*)(std::basic_ofstream<char,std::char_traits<char> >&) const)&PLib::NurbsCurve<double,3>::write)
        .def("writePS", &PLib::NurbsCurve<double,3>::writePS, NurbsCurve3Dd_writePS_overloads_1_5())
        .def("writePSp", &PLib::NurbsCurve<double,3>::writePSp, NurbsCurve3Dd_writePSp_overloads_3_7())
//         .def("writeVRML", (int (PLib::NurbsCurve<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,3>::writeVRML)
        .def("writeVRML", (int (PLib::NurbsCurve<double,3>::*)(const char*, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,3>::writeVRML)
        .def("writeVRML", (int (PLib::NurbsCurve<double,3>::*)(const char*, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,3>::writeVRML, NurbsCurve3Dd_writeVRML_overloads_1_6())
//         .def("writeVRML", (int (PLib::NurbsCurve<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,3>::writeVRML, NurbsCurve3Dd_writeVRML_overloads_1_6())
        .def("writeVRML97", (int (PLib::NurbsCurve<double,3>::*)(const char*, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,3>::writeVRML97)
//         .def("writeVRML97", (int (PLib::NurbsCurve<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int, double, double) const)&PLib::NurbsCurve<double,3>::writeVRML97)
        .def("writeVRML97", (int (PLib::NurbsCurve<double,3>::*)(const char*, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,3>::writeVRML97, NurbsCurve3Dd_writeVRML97_overloads_1_6())
//         .def("writeVRML97", (int (PLib::NurbsCurve<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, double, int, const PLib::Color&, int, int) const)&PLib::NurbsCurve<double,3>::writeVRML97, NurbsCurve3Dd_writeVRML97_overloads_1_6())
        .def("writeDisplayLINE", (int (PLib::NurbsCurve<double,3>::*)(const char*, int, const PLib::Color&, double) const)&PLib::NurbsCurve<double,3>::writeDisplayLINE, NurbsCurve3Dd_writeDisplayLINE_overloads_2_4())
        .def("writeDisplayLINE", (int (PLib::NurbsCurve<double,3>::*)(const char*, const PLib::Color&, int, double, double) const)&PLib::NurbsCurve<double,3>::writeDisplayLINE)
        .def("drawImg", (void (PLib::NurbsCurve<double,3>::*)(PLib::MatrixImage<unsigned char>&, unsigned char, double) )&PLib::NurbsCurve<double,3>::drawImg, NurbsCurve3Dd_drawImg_overloads_1_3())
        .def("drawImg", (void (PLib::NurbsCurve<double,3>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, double) )&PLib::NurbsCurve<double,3>::drawImg, NurbsCurve3Dd_drawImg_overloads_2_3())
        .def("drawAaImg", (void (PLib::NurbsCurve<double,3>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, int, int) )&PLib::NurbsCurve<double,3>::drawAaImg, NurbsCurve3Dd_drawAaImg_overloads_2_4())
        .def("drawAaImg", (void (PLib::NurbsCurve<double,3>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, const PLib::NurbsCurve<double,3>&, int, int) )&PLib::NurbsCurve<double,3>::drawAaImg, NurbsCurve3Dd_drawAaImg_overloads_3_5())
        .def("drawAaImg", (PLib::NurbsSurface<double,3> (PLib::NurbsCurve<double,3>::*)(PLib::MatrixImage<PLib::Color>&, const PLib::Color&, const PLib::NurbsCurve<double,3>&, const PLib::NurbsCurve<double,3>&, int, int) )&PLib::NurbsCurve<double,3>::drawAaImg, NurbsCurve3Dd_drawAaImg_overloads_4_6())
        .def("tesselate", &PLib::NurbsCurve<double,3>::tesselate)
        .def("pointAt", (PLib::Point_nD<double,3> (PLib::ParaCurve<double,3>::*)(double) const)&PLib::ParaCurve<double,3>::pointAt)
        .def("pointAt", (PLib::Point_nD<double,3> (PLib::ParaCurve<double,3>::*)(double, int) )&PLib::ParaCurve<double,3>::pointAt)
        .def("__call__", &PLib::NurbsCurve<double,3>::operator ())
    ;

}

