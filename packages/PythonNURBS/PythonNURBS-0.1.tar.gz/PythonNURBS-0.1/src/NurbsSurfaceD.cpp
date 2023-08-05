/**************************************************************************
*   Copyright (C) 2008-2008 by Oliver Borm                                *
*   oli.borm@web.de                                                       *
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

/** Author: Oliver Borm
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

struct NurbsSurfaced_Wrapper: PLib::NurbsSurface<double,3>
{
    NurbsSurfaced_Wrapper(PyObject* py_self_):
        PLib::NurbsSurface<double,3>(), py_self(py_self_) {}

    NurbsSurfaced_Wrapper(PyObject* py_self_, const PLib::NurbsSurface<double,3>& p0):
        PLib::NurbsSurface<double,3>(p0), py_self(py_self_) {}

    NurbsSurfaced_Wrapper(PyObject* py_self_, int p0, int p1, const PLib::Vector<double>& p2, const PLib::Vector<double>& p3, const PLib::Matrix<PLib::HPoint_nD<double, 3> >& p4):
        PLib::NurbsSurface<double,3>(p0, p1, p2, p3, p4), py_self(py_self_) {}

    NurbsSurfaced_Wrapper(PyObject* py_self_, int p0, int p1, PLib::Vector<double>& p2, PLib::Vector<double>& p3, PLib::Matrix<PLib::Point_nD<double, 3> >& p4, PLib::Matrix<double>& p5):
        PLib::NurbsSurface<double,3>(p0, p1, p2, p3, p4, p5), py_self(py_self_) {}

    void resizeKeep(int p0, int p1, int p2, int p3) {
        call_method< void >(py_self, "resizeKeep", p0, p1, p2, p3);
    }

    void default_resizeKeep(int p0, int p1, int p2, int p3) {
        PLib::NurbsSurface<double,3>::resizeKeep(p0, p1, p2, p3);
    }

    void deriveAt(double p0, double p1, int p2, PLib::Matrix<PLib::Point_nD<double, 3> >& p3) const {
        call_method< void >(py_self, "deriveAt", p0, p1, p2, p3);
    }

    void default_deriveAt(double p0, double p1, int p2, PLib::Matrix<PLib::Point_nD<double, 3> >& p3) const {
        PLib::NurbsSurface<double,3>::deriveAt(p0, p1, p2, p3);
    }

    void deriveAtH(double p0, double p1, int p2, PLib::Matrix<PLib::HPoint_nD<double, 3> >& p3) const {
        call_method< void >(py_self, "deriveAtH", p0, p1, p2, p3);
    }

    void default_deriveAtH(double p0, double p1, int p2, PLib::Matrix<PLib::HPoint_nD<double, 3> >& p3) const {
        PLib::NurbsSurface<double,3>::deriveAtH(p0, p1, p2, p3);
    }

    void degreeElevateU(int p0) {
        call_method< void >(py_self, "degreeElevateU", p0);
    }

    void default_degreeElevateU(int p0) {
        PLib::NurbsSurface<double,3>::degreeElevateU(p0);
    }

    void degreeElevateV(int p0) {
        call_method< void >(py_self, "degreeElevateV", p0);
    }

    void default_degreeElevateV(int p0) {
        PLib::NurbsSurface<double,3>::degreeElevateV(p0);
    }

    void refineKnots(const PLib::Vector<double>& p0, const PLib::Vector<double>& p1) {
        call_method< void >(py_self, "refineKnots", p0, p1);
    }

    void default_refineKnots(const PLib::Vector<double>& p0, const PLib::Vector<double>& p1) {
        PLib::NurbsSurface<double,3>::refineKnots(p0, p1);
    }

    void refineKnotU(const PLib::Vector<double>& p0) {
        call_method< void >(py_self, "refineKnotU", p0);
    }

    void default_refineKnotU(const PLib::Vector<double>& p0) {
        PLib::NurbsSurface<double,3>::refineKnotU(p0);
    }

    void refineKnotV(const PLib::Vector<double>& p0) {
        call_method< void >(py_self, "refineKnotV", p0);
    }

    void default_refineKnotV(const PLib::Vector<double>& p0) {
        PLib::NurbsSurface<double,3>::refineKnotV(p0);
    }

    void mergeKnots(const PLib::Vector<double>& p0, const PLib::Vector<double>& p1) {
        call_method< void >(py_self, "mergeKnots", p0, p1);
    }

    void default_mergeKnots(const PLib::Vector<double>& p0, const PLib::Vector<double>& p1) {
        PLib::NurbsSurface<double,3>::mergeKnots(p0, p1);
    }

    void mergeKnotU(const PLib::Vector<double>& p0) {
        call_method< void >(py_self, "mergeKnotU", p0);
    }

    void default_mergeKnotU(const PLib::Vector<double>& p0) {
        PLib::NurbsSurface<double,3>::mergeKnotU(p0);
    }

    void mergeKnotV(const PLib::Vector<double>& p0) {
        call_method< void >(py_self, "mergeKnotV", p0);
    }

    void default_mergeKnotV(const PLib::Vector<double>& p0) {
        PLib::NurbsSurface<double,3>::mergeKnotV(p0);
    }

    int read(std::basic_ifstream<char,std::char_traits<char> >& p0) {
        return call_method< int >(py_self, "read", p0);
    }

    int default_read(std::basic_ifstream<char,std::char_traits<char> >& p0) {
        return PLib::NurbsSurface<double,3>::read(p0);
    }

    int writeVRML(const char* p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
        return call_method< int >(py_self, "writeVRML", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    int default_writeVRML(const char* p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
        return PLib::NurbsSurface<double,3>::writeVRML(p0, p1, p2, p3, p4, p5, p6, p7);
    }

//     int writeVRML(std::basic_ostream<char,std::char_traits<char> >& p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
//         return call_method< int >(py_self, "writeVRML", p0, p1, p2, p3, p4, p5, p6, p7);
//     }

//     int default_writeVRML(std::basic_ostream<char,std::char_traits<char> >& p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
//         return PLib::NurbsSurface<double,3>::writeVRML(p0, p1, p2, p3, p4, p5, p6, p7);
//     }

    int writeVRML97(const char* p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
        return call_method< int >(py_self, "writeVRML97", p0, p1, p2, p3, p4, p5, p6, p7);
    }

    int default_writeVRML97(const char* p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
        return PLib::NurbsSurface<double,3>::writeVRML97(p0, p1, p2, p3, p4, p5, p6, p7);
    }

//     int writeVRML97(std::basic_ostream<char,std::char_traits<char> >& p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
//         return call_method< int >(py_self, "writeVRML97", p0, p1, p2, p3, p4, p5, p6, p7);
//     }

//     int default_writeVRML97(std::basic_ostream<char,std::char_traits<char> >& p0, const PLib::Color& p1, int p2, int p3, double p4, double p5, double p6, double p7) const {
//         return PLib::NurbsSurface<double,3>::writeVRML97(p0, p1, p2, p3, p4, p5, p6, p7);
//     }

    int writeVRML(const char* p0, const PLib::Color& p1, int p2, int p3) const {
        return call_method< int >(py_self, "writeVRML", p0, p1, p2, p3);
    }

    int default_writeVRML_1(const char* p0) const {
        return PLib::NurbsSurface<double,3>::writeVRML(p0);
    }

    int default_writeVRML_2(const char* p0, const PLib::Color& p1) const {
        return PLib::NurbsSurface<double,3>::writeVRML(p0, p1);
    }

    int default_writeVRML_3(const char* p0, const PLib::Color& p1, int p2) const {
        return PLib::NurbsSurface<double,3>::writeVRML(p0, p1, p2);
    }

    int default_writeVRML_4(const char* p0, const PLib::Color& p1, int p2, int p3) const {
        return PLib::NurbsSurface<double,3>::writeVRML(p0, p1, p2, p3);
    }

    int writeVRML97(const char* p0, const PLib::Color& p1, int p2, int p3) const {
        return call_method< int >(py_self, "writeVRML97", p0, p1, p2, p3);
    }

    int default_writeVRML97_1(const char* p0) const {
        return PLib::NurbsSurface<double,3>::writeVRML97(p0);
    }

    int default_writeVRML97_2(const char* p0, const PLib::Color& p1) const {
        return PLib::NurbsSurface<double,3>::writeVRML97(p0, p1);
    }

    int default_writeVRML97_3(const char* p0, const PLib::Color& p1, int p2) const {
        return PLib::NurbsSurface<double,3>::writeVRML97(p0, p1, p2);
    }

    int default_writeVRML97_4(const char* p0, const PLib::Color& p1, int p2, int p3) const {
        return PLib::NurbsSurface<double,3>::writeVRML97(p0, p1, p2, p3);
    }

    double minDist2(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8, double p9, double p10) const {
        return call_method< double >(py_self, "minDist2", p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10);
    }

    double default_minDist2_3(const PLib::Point_nD<double,3>& p0, double& p1, double& p2) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2);
    }

    double default_minDist2_4(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3);
    }

    double default_minDist2_5(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3, p4);
    }

    double default_minDist2_6(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3, p4, p5);
    }

    double default_minDist2_7(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3, p4, p5, p6);
    }

    double default_minDist2_8(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    double default_minDist2_9(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3, p4, p5, p6, p7, p8);
    }

    double default_minDist2_10(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8, double p9) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9);
    }

    double default_minDist2_11(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8, double p9, double p10) const {
        return PLib::ParaSurface<double,3>::minDist2(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10);
    }

    double minDist2b(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8, double p9, double p10) const {
        return call_method< double >(py_self, "minDist2b", p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10);
    }

    double default_minDist2b_3(const PLib::Point_nD<double,3>& p0, double& p1, double& p2) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2);
    }

    double default_minDist2b_4(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3);
    }

    double default_minDist2b_5(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3, p4);
    }

    double default_minDist2b_6(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3, p4, p5);
    }

    double default_minDist2b_7(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3, p4, p5, p6);
    }

    double default_minDist2b_8(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    double default_minDist2b_9(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3, p4, p5, p6, p7, p8);
    }

    double default_minDist2b_10(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8, double p9) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9);
    }

    double default_minDist2b_11(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, int p5, int p6, double p7, double p8, double p9, double p10) const {
        return PLib::ParaSurface<double,3>::minDist2b(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10);
    }

    double minDist2xy(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6, int p7, int p8, double p9, double p10, double p11, double p12) const {
        return call_method< double >(py_self, "minDist2xy", p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12);
    }

    double default_minDist2xy_3(const PLib::Point_nD<double,3>& p0, double& p1, double& p2) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2);
    }

    double default_minDist2xy_4(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3);
    }

    double default_minDist2xy_5(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4);
    }

    double default_minDist2xy_6(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5);
    }

    double default_minDist2xy_7(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5, p6);
    }

    double default_minDist2xy_8(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6, int p7) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5, p6, p7);
    }

    double default_minDist2xy_9(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6, int p7, int p8) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5, p6, p7, p8);
    }

    double default_minDist2xy_10(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6, int p7, int p8, double p9) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9);
    }

    double default_minDist2xy_11(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6, int p7, int p8, double p9, double p10) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10);
    }

    double default_minDist2xy_12(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6, int p7, int p8, double p9, double p10, double p11) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11);
    }

    double default_minDist2xy_13(const PLib::Point_nD<double,3>& p0, double& p1, double& p2, double p3, double p4, double p5, int p6, int p7, int p8, double p9, double p10, double p11, double p12) const {
        return PLib::ParaSurface<double,3>::minDist2xy(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_sweep_overloads_4_6, sweep, 4, 6)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_sweep_overloads_3_5, sweep, 3, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_area_overloads_0_2, area, 0, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writeVRML_overloads_1_4, writeVRML, 1, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writeVRML97_overloads_1_4, writeVRML97, 1, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writePOVRAY_overloads_1_5, writePOVRAY, 1, 5)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writePOVRAY_overloads_2_6, writePOVRAY, 2, 6)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writePOVRAY_overloads_4_8, writePOVRAY, 4, 8)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writePOVRAY_overloads_5_8, writePOVRAY, 5, 8)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_tesselate_overloads_3_4, tesselate, 3, 4)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writePS_overloads_5_8, writePS, 5, 8)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writePSp_overloads_7_10, writePSp, 7, 10)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writeOOGL_overloads_3_8, writeOOGL, 3, 8)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(NurbsSurfaced_writeDisplayQUADMESH_overloads_1_6, writeDisplayQUADMESH, 1, 6)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_ParaSurface_double_3_projectOn_overloads_3_8, projectOn, 3, 8)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_ParaSurface_double_3_extremum_overloads_2_10, extremum, 2, 10)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_ParaSurface_double_3_intersectWith_overloads_6_11, intersectWith, 6, 11)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_ParaSurface_double_3_intersectWith_overloads_2_7, intersectWith, 2, 7)


}// namespace 


// Module ======================================================================
BOOST_PYTHON_MODULE(NurbsSurfaceD)
{
    class_< PLib::NurbsSurface<double,3>, NurbsSurfaced_Wrapper >("NurbsSurfaced", init<  >())
        .def(init< const PLib::NurbsSurface<double,3>& >())
        .def(init< int, int, const PLib::Vector<double>&, const PLib::Vector<double>&, const PLib::Matrix<PLib::HPoint_nD<double, 3> >& >())
        .def(init< int, int, PLib::Vector<double>&, PLib::Vector<double>&, PLib::Matrix<PLib::Point_nD<double, 3> >&, PLib::Matrix<double>& >())
//         .def("resizeKeep", &PLib::NurbsSurface<double,3>::resizeKeep, &NurbsSurfaced_Wrapper::default_resizeKeep)
        .def("deriveAt", (void (PLib::NurbsSurface<double,3>::*)(double, double, int, PLib::Matrix<PLib::Point_nD<double, 3> >&) const)&PLib::NurbsSurface<double,3>::deriveAt, (void (NurbsSurfaced_Wrapper::*)(double, double, int, PLib::Matrix<PLib::Point_nD<double, 3> >&) const)&NurbsSurfaced_Wrapper::default_deriveAt)
        .def("deriveAtH", (void (PLib::NurbsSurface<double,3>::*)(double, double, int, PLib::Matrix<PLib::HPoint_nD<double, 3> >&) const)&PLib::NurbsSurface<double,3>::deriveAtH, (void (NurbsSurfaced_Wrapper::*)(double, double, int, PLib::Matrix<PLib::HPoint_nD<double, 3> >&) const)&NurbsSurfaced_Wrapper::default_deriveAtH)
        .def("degreeElevateU", &PLib::NurbsSurface<double,3>::degreeElevateU, &NurbsSurfaced_Wrapper::default_degreeElevateU)
        .def("degreeElevateV", &PLib::NurbsSurface<double,3>::degreeElevateV, &NurbsSurfaced_Wrapper::default_degreeElevateV)
        .def("refineKnots", &PLib::NurbsSurface<double,3>::refineKnots, &NurbsSurfaced_Wrapper::default_refineKnots)
        .def("refineKnotU", &PLib::NurbsSurface<double,3>::refineKnotU, &NurbsSurfaced_Wrapper::default_refineKnotU)
        .def("refineKnotV", &PLib::NurbsSurface<double,3>::refineKnotV, &NurbsSurfaced_Wrapper::default_refineKnotV)
        .def("mergeKnots", &PLib::NurbsSurface<double,3>::mergeKnots, &NurbsSurfaced_Wrapper::default_mergeKnots)
        .def("mergeKnotU", &PLib::NurbsSurface<double,3>::mergeKnotU, &NurbsSurfaced_Wrapper::default_mergeKnotU)
        .def("mergeKnotV", &PLib::NurbsSurface<double,3>::mergeKnotV, &NurbsSurfaced_Wrapper::default_mergeKnotV)
        .def("read", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ifstream<char,std::char_traits<char> >&) )&PLib::NurbsSurface<double,3>::read, (int (NurbsSurfaced_Wrapper::*)(std::basic_ifstream<char,std::char_traits<char> >&))&NurbsSurfaced_Wrapper::default_read)
        .def("writeVRML", (int (PLib::NurbsSurface<double,3>::*)(const char*, const PLib::Color&, int, int, double, double, double, double) const)&PLib::NurbsSurface<double,3>::writeVRML, (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&, int, int, double, double, double, double) const)&NurbsSurfaced_Wrapper::default_writeVRML)
        .def("writeVRML", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, const PLib::Color&, int, int, double, double, double, double) const)&PLib::NurbsSurface<double,3>::writeVRML, (int (NurbsSurfaced_Wrapper::*)(std::basic_ostream<char,std::char_traits<char> >&, const PLib::Color&, int, int, double, double, double, double) const)&NurbsSurfaced_Wrapper::default_writeVRML)
        .def("writeVRML97", (int (PLib::NurbsSurface<double,3>::*)(const char*, const PLib::Color&, int, int, double, double, double, double) const)&PLib::NurbsSurface<double,3>::writeVRML97, (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&, int, int, double, double, double, double) const)&NurbsSurfaced_Wrapper::default_writeVRML97)
        .def("writeVRML97", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, const PLib::Color&, int, int, double, double, double, double) const)&PLib::NurbsSurface<double,3>::writeVRML97, (int (NurbsSurfaced_Wrapper::*)(std::basic_ostream<char,std::char_traits<char> >&, const PLib::Color&, int, int, double, double, double, double) const)&NurbsSurfaced_Wrapper::default_writeVRML97)
        .def("writeVRML", (int (PLib::NurbsSurface<double,3>::*)(const char*, const PLib::Color&, int, int) const)&PLib::NurbsSurface<double,3>::writeVRML, (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&, int, int) const)&NurbsSurfaced_Wrapper::default_writeVRML_4)
        .def("writeVRML", (int (NurbsSurfaced_Wrapper::*)(const char*) const)&NurbsSurfaced_Wrapper::default_writeVRML_1)
        .def("writeVRML", (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&) const)&NurbsSurfaced_Wrapper::default_writeVRML_2)
        .def("writeVRML", (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&, int) const)&NurbsSurfaced_Wrapper::default_writeVRML_3)
        .def("writeVRML97", (int (PLib::NurbsSurface<double,3>::*)(const char*, const PLib::Color&, int, int) const)&PLib::NurbsSurface<double,3>::writeVRML97, (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&, int, int) const)&NurbsSurfaced_Wrapper::default_writeVRML97_4)
        .def("writeVRML97", (int (NurbsSurfaced_Wrapper::*)(const char*) const)&NurbsSurfaced_Wrapper::default_writeVRML97_1)
        .def("writeVRML97", (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&) const)&NurbsSurfaced_Wrapper::default_writeVRML97_2)
        .def("writeVRML97", (int (NurbsSurfaced_Wrapper::*)(const char*, const PLib::Color&, int) const)&NurbsSurfaced_Wrapper::default_writeVRML97_3)
        .def("minDist2", (double (PLib::ParaSurface<double,3>::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double, double, double) const)&PLib::ParaSurface<double,3>::minDist2, (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2_11)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&) const)&NurbsSurfaced_Wrapper::default_minDist2_3)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double) const)&NurbsSurfaced_Wrapper::default_minDist2_4)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2_5)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int) const)&NurbsSurfaced_Wrapper::default_minDist2_6)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int) const)&NurbsSurfaced_Wrapper::default_minDist2_7)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double) const)&NurbsSurfaced_Wrapper::default_minDist2_8)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2_9)
        .def("minDist2", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2_10)
        .def("minDist2b", (double (PLib::ParaSurface<double,3>::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double, double, double) const)&PLib::ParaSurface<double,3>::minDist2b, (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2b_11)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&) const)&NurbsSurfaced_Wrapper::default_minDist2b_3)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double) const)&NurbsSurfaced_Wrapper::default_minDist2b_4)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2b_5)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int) const)&NurbsSurfaced_Wrapper::default_minDist2b_6)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int) const)&NurbsSurfaced_Wrapper::default_minDist2b_7)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double) const)&NurbsSurfaced_Wrapper::default_minDist2b_8)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2b_9)
        .def("minDist2b", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, int, int, double, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2b_10)
        .def("minDist2xy", (double (PLib::ParaSurface<double,3>::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int, int, int, double, double, double, double) const)&PLib::ParaSurface<double,3>::minDist2xy, (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int, int, int, double, double, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2xy_13)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&) const)&NurbsSurfaced_Wrapper::default_minDist2xy_3)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double) const)&NurbsSurfaced_Wrapper::default_minDist2xy_4)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2xy_5)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2xy_6)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int) const)&NurbsSurfaced_Wrapper::default_minDist2xy_7)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int, int) const)&NurbsSurfaced_Wrapper::default_minDist2xy_8)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int, int, int) const)&NurbsSurfaced_Wrapper::default_minDist2xy_9)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int, int, int, double) const)&NurbsSurfaced_Wrapper::default_minDist2xy_10)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int, int, int, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2xy_11)
        .def("minDist2xy", (double (NurbsSurfaced_Wrapper::*)(const PLib::Point_nD<double,3>&, double&, double&, double, double, double, int, int, int, double, double, double) const)&NurbsSurfaced_Wrapper::default_minDist2xy_12)
//         .def("knotU", (const PLib::Vector<double>& (PLib::NurbsSurface<double,3>::*)() const)&PLib::NurbsSurface<double,3>::knotU, return_value_policy< copy_const_reference >())
//         .def("knotV", (const PLib::Vector<double>& (PLib::NurbsSurface<double,3>::*)() const)&PLib::NurbsSurface<double,3>::knotV, return_value_policy< copy_const_reference >())
//         .def("knotU", (double (PLib::NurbsSurface<double,3>::*)(int) const)&PLib::NurbsSurface<double,3>::knotU, return_value_policy< copy_const_reference >())
//         .def("knotV", (double (PLib::NurbsSurface<double,3>::*)(int) const)&PLib::NurbsSurface<double,3>::knotV, return_value_policy< copy_const_reference >())
//         .def("ctrlPnts", (const PLib::Matrix<PLib::HPoint_nD<double, 3> >& (PLib::NurbsSurface<double,3>::*)() const)&PLib::NurbsSurface<double,3>::ctrlPnts, return_value_policy< copy_const_reference >())
//         .def("ctrlPnts", (const PLib::HPoint_nD<double,3> (PLib::NurbsSurface<double,3>::*)(int, int) const)&PLib::NurbsSurface<double,3>::ctrlPnts, return_value_policy< copy_const_reference >())
        .def("degreeU", &PLib::NurbsSurface<double,3>::degreeU)
        .def("degreeV", &PLib::NurbsSurface<double,3>::degreeV)
        .def("resize", &PLib::NurbsSurface<double,3>::resize)
        .def("ok", &PLib::NurbsSurface<double,3>::ok)
        .def("basisFuns", &PLib::NurbsSurface<double,3>::basisFuns)
        .def("basisFunsU", &PLib::NurbsSurface<double,3>::basisFunsU)
        .def("basisFunsV", &PLib::NurbsSurface<double,3>::basisFunsV)
        .def("dersBasisFuns", &PLib::NurbsSurface<double,3>::dersBasisFuns)
        .def("normal", &PLib::NurbsSurface<double,3>::normal)
        .def("globalInterp", &PLib::NurbsSurface<double,3>::globalInterp)
        .def("globalInterpH", &PLib::NurbsSurface<double,3>::globalInterpH)
        .def("globalInterpClosedU", &PLib::NurbsSurface<double,3>::globalInterpClosedU)
        .def("globalInterpClosedUH", &PLib::NurbsSurface<double,3>::globalInterpClosedUH)
        .def("leastSquares", &PLib::NurbsSurface<double,3>::leastSquares)
        .def("leastSquaresClosedU", &PLib::NurbsSurface<double,3>::leastSquaresClosedU)
        .def("skinV", &PLib::NurbsSurface<double,3>::skinV)
        .def("skinU", &PLib::NurbsSurface<double,3>::skinU)
        .def("sweep", (void (PLib::NurbsSurface<double,3>::*)(const PLib::NurbsCurve<double,3>&, const PLib::NurbsCurve<double,3>&, const PLib::NurbsCurve<double,3>&, int, int, int) )&PLib::NurbsSurface<double,3>::sweep, NurbsSurfaced_sweep_overloads_4_6())
        .def("sweep", (void (PLib::NurbsSurface<double,3>::*)(const PLib::NurbsCurve<double,3>&, const PLib::NurbsCurve<double,3>&, int, int, int) )&PLib::NurbsSurface<double,3>::sweep, NurbsSurfaced_sweep_overloads_3_5())
        .def("makeFromRevolution", (void (PLib::NurbsSurface<double,3>::*)(const PLib::NurbsCurve<double,3>&, const PLib::Point_nD<double,3>&, const PLib::Point_nD<double,3>&, double) )&PLib::NurbsSurface<double,3>::makeFromRevolution)
        .def("makeFromRevolution", (void (PLib::NurbsSurface<double,3>::*)(const PLib::NurbsCurve<double,3>&, const PLib::Point_nD<double,3>&, const PLib::Point_nD<double,3>&) )&PLib::NurbsSurface<double,3>::makeFromRevolution)
        .def("makeFromRevolution", (void (PLib::NurbsSurface<double,3>::*)(const PLib::NurbsCurve<double,3>&) )&PLib::NurbsSurface<double,3>::makeFromRevolution)
        .def("makeSphere", &PLib::NurbsSurface<double,3>::makeSphere)
        .def("makeTorus", &PLib::NurbsSurface<double,3>::makeTorus)
        .def("degreeElevate", &PLib::NurbsSurface<double,3>::degreeElevate)
        .def("decompose", &PLib::NurbsSurface<double,3>::decompose)
        .def("findSpan", &PLib::NurbsSurface<double,3>::findSpan)
        .def("findSpanU", &PLib::NurbsSurface<double,3>::findSpanU)
        .def("findSpanV", &PLib::NurbsSurface<double,3>::findSpanV)
        .def("findMultU", &PLib::NurbsSurface<double,3>::findMultU)
        .def("findMultV", &PLib::NurbsSurface<double,3>::findMultV)
        .def("area", &PLib::NurbsSurface<double,3>::area, NurbsSurfaced_area_overloads_0_2())
        .def("areaIn", &PLib::NurbsSurface<double,3>::areaIn)
        .def("areaF", &PLib::NurbsSurface<double,3>::areaF)
        .def("isoCurveU", &PLib::NurbsSurface<double,3>::isoCurveU)
        .def("isoCurveV", &PLib::NurbsSurface<double,3>::isoCurveV)
        .def("read", (int (PLib::NurbsSurface<double,3>::*)(const char*) )&PLib::NurbsSurface<double,3>::read)
        .def("write", (int (PLib::NurbsSurface<double,3>::*)(const char*) const)&PLib::NurbsSurface<double,3>::write)
        .def("write", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ofstream<char,std::char_traits<char> >&) const)&PLib::NurbsSurface<double,3>::write)
//         .def("print", &PLib::NurbsSurface<double,3>::print)
        .def("writeVRML", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, const PLib::Color&, int, int) const)&PLib::NurbsSurface<double,3>::writeVRML, NurbsSurfaced_writeVRML_overloads_1_4())
        .def("writeVRML97", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, const PLib::Color&, int, int) const)&PLib::NurbsSurface<double,3>::writeVRML97, NurbsSurfaced_writeVRML97_overloads_1_4())
        .def("writePOVRAY", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&, int, double, int, int) const)&PLib::NurbsSurface<double,3>::writePOVRAY, NurbsSurfaced_writePOVRAY_overloads_1_5())
        .def("writePOVRAY", (int (PLib::NurbsSurface<double,3>::*)(double, std::basic_ostream<char,std::char_traits<char> >&, const PLib::Color&, int, double, double) const)&PLib::NurbsSurface<double,3>::writePOVRAY, NurbsSurfaced_writePOVRAY_overloads_2_6())
        .def("writePOVRAY", (int (PLib::NurbsSurface<double,3>::*)(const char*, const PLib::Color&, const PLib::Point_nD<double,3>&, const PLib::Point_nD<double,3>&, int, double, int, int) const)&PLib::NurbsSurface<double,3>::writePOVRAY, NurbsSurfaced_writePOVRAY_overloads_4_8())
        .def("writePOVRAY", (int (PLib::NurbsSurface<double,3>::*)(double, const char*, const PLib::Color&, const PLib::Point_nD<double,3>&, const PLib::Point_nD<double,3>&, int, double, double) const)&PLib::NurbsSurface<double,3>::writePOVRAY, NurbsSurfaced_writePOVRAY_overloads_5_8())
        .def("writeRIB", (int (PLib::NurbsSurface<double,3>::*)(std::basic_ostream<char,std::char_traits<char> >&) const)&PLib::NurbsSurface<double,3>::writeRIB)
        .def("writeRIB", (int (PLib::NurbsSurface<double,3>::*)(const char*, const PLib::Color&, const PLib::Point_nD<double,3>&) const)&PLib::NurbsSurface<double,3>::writeRIB)
        .def("tesselate", &PLib::NurbsSurface<double,3>::tesselate, NurbsSurfaced_tesselate_overloads_3_4())
        .def("writePS", &PLib::NurbsSurface<double,3>::writePS, NurbsSurfaced_writePS_overloads_5_8())
        .def("writePSp", &PLib::NurbsSurface<double,3>::writePSp, NurbsSurfaced_writePSp_overloads_7_10())
        .def("writeOOGL", (int (PLib::NurbsSurface<double,3>::*)(const char*, double, double, double, double, double, double, bool) const)&PLib::NurbsSurface<double,3>::writeOOGL, NurbsSurfaced_writeOOGL_overloads_3_8())
        .def("writeOOGL", (int (PLib::NurbsSurface<double,3>::*)(const char*) const)&PLib::NurbsSurface<double,3>::writeOOGL)
        .def("writeDisplayQUADMESH", &PLib::NurbsSurface<double,3>::writeDisplayQUADMESH, NurbsSurfaced_writeDisplayQUADMESH_overloads_1_6())
        .def("transform", &PLib::NurbsSurface<double,3>::transform)
        .def("modCP", &PLib::NurbsSurface<double,3>::modCP)
        .def("modCPby", &PLib::NurbsSurface<double,3>::modCPby)
//         .def("modU", (double& (PLib::NurbsSurface<double,3>::*)(int) )&PLib::NurbsSurface<double,3>::modU)
        .def("modU", (double (PLib::NurbsSurface<double,3>::*)(int) const)&PLib::NurbsSurface<double,3>::modU)
//         .def("modV", (double& (PLib::NurbsSurface<double,3>::*)(int) )&PLib::NurbsSurface<double,3>::modV)
        .def("modV", (double (PLib::NurbsSurface<double,3>::*)(int) const)&PLib::NurbsSurface<double,3>::modV)
        .def("modKnotU", &PLib::NurbsSurface<double,3>::modKnotU)
        .def("modKnotV", &PLib::NurbsSurface<double,3>::modKnotV)
        .def("movePoint", (int (PLib::NurbsSurface<double,3>::*)(double, double, const PLib::Point_nD<double,3>&) )&PLib::NurbsSurface<double,3>::movePoint)
        .def("movePoint", (int (PLib::NurbsSurface<double,3>::*)(const PLib::Vector<double>&, const PLib::Vector<double>&, const PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<int>&, const PLib::Vector<int>&) )&PLib::NurbsSurface<double,3>::movePoint)
        .def("movePoint", (int (PLib::NurbsSurface<double,3>::*)(const PLib::Vector<double>&, const PLib::Vector<double>&, const PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<int>&, const PLib::Vector<int>&, const PLib::Vector<int>&, const PLib::Vector<int>&) )&PLib::NurbsSurface<double,3>::movePoint)
        .def("movePoint", (int (PLib::NurbsSurface<double,3>::*)(const PLib::Vector<double>&, const PLib::Vector<double>&, const PLib::Vector<PLib::Point_nD<double, 3> >&, const PLib::Vector<int>&, const PLib::Vector<int>&, const PLib::Vector<int>&, const PLib::Vector<int>&, const PLib::BasicArray<PLib::Coordinate>&) )&PLib::NurbsSurface<double,3>::movePoint)
//         .def("transpose", &PLib::NurbsSurface<double,3>::transpose)
        .def("hpointAt", &PLib::ParaSurface<double,3>::hpointAt)
        .def("pointAt", &PLib::ParaSurface<double,3>::pointAt)
        .def("projectOn", &PLib::ParaSurface<double,3>::projectOn, PLib_ParaSurface_double_3_projectOn_overloads_3_8())
        .def("extremum", &PLib::ParaSurface<double,3>::extremum, PLib_ParaSurface_double_3_extremum_overloads_2_10())
        .def("intersectWith", (int (PLib::ParaSurface<double,3>::*)(const PLib::ParaSurface<double,3>&, PLib::Point_nD<double,3>&, double&, double&, double&, double&, int, double, double, double, double) const)&PLib::ParaSurface<double,3>::intersectWith, PLib_ParaSurface_double_3_intersectWith_overloads_6_11())
        .def("intersectWith", (int (PLib::ParaSurface<double,3>::*)(const PLib::ParaSurface<double,3>&, PLib::InterPoint<double,3>&, int, double, double, double, double) const)&PLib::ParaSurface<double,3>::intersectWith, PLib_ParaSurface_double_3_intersectWith_overloads_2_7())
        .def("__call__", &PLib::NurbsSurface<double,3>::operator ())
    ;

}

