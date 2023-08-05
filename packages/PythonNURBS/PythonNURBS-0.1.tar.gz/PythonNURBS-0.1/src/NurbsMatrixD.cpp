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
#include <nurbs++/matrix.h>

// Using =======================================================================
using namespace boost::python;

// Declarations ================================================================
namespace  {

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_Basic2DArray_PLib_Point_nD_double_3_reset_overloads_0_1, reset, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_Basic2DArray_PLib_Point_nD_double_2_reset_overloads_0_1, reset, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_Basic2DArray_PLib_HPoint_nD_double_3_reset_overloads_0_1, reset, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_Basic2DArray_PLib_HPoint_nD_double_2_reset_overloads_0_1, reset, 0, 1)

// struct PLib_BasicArray_PLib_Point_nD_double_3_Wrapper: PLib::BasicArray<PLib::Point_nD<double, 3> >
// {
//     PLib_BasicArray_PLib_Point_nD_double_3_Wrapper(PyObject* py_self_):
//         PLib::BasicArray<PLib::Point_nD<double, 3> >(), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_3_Wrapper(PyObject* py_self_, const int p0):
//         PLib::BasicArray<PLib::Point_nD<double, 3> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_3_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::Point_nD<double, 3> >& p0):
//         PLib::BasicArray<PLib::Point_nD<double, 3> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_3_Wrapper(PyObject* py_self_, PLib::Point_nD<double,3>* p0, const int p1):
//         PLib::BasicArray<PLib::Point_nD<double, 3> >(p0, p1), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_3_Wrapper(PyObject* py_self_, BasicList<PLib::Point_nD<double, 3> >& p0):
//         PLib::BasicArray<PLib::Point_nD<double, 3> >(p0), py_self(py_self_) {}
// 
//     void reset(const PLib::Point_nD<double,3> p0) {
//         call_method< void >(py_self, "reset", p0);
//     }
// 
//     void default_reset_0() {
//         PLib::BasicArray<PLib::Point_nD<double, 3> >::reset();
//     }
// 
//     void default_reset_1(const PLib::Point_nD<double,3> p0) {
//         PLib::BasicArray<PLib::Point_nD<double, 3> >::reset(p0);
//     }
// 
//     PyObject* py_self;
// };

// BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_BasicArray_PLib_Point_nD_double_3_push_back_overloads_1_3, push_back, 1, 3)

// struct PLib_BasicArray_PLib_Point_nD_double_2_Wrapper: PLib::BasicArray<PLib::Point_nD<double, 2> >
// {
//     PLib_BasicArray_PLib_Point_nD_double_2_Wrapper(PyObject* py_self_):
//         PLib::BasicArray<PLib::Point_nD<double, 2> >(), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_2_Wrapper(PyObject* py_self_, const int p0):
//         PLib::BasicArray<PLib::Point_nD<double, 2> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_2_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::Point_nD<double, 2> >& p0):
//         PLib::BasicArray<PLib::Point_nD<double, 2> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_2_Wrapper(PyObject* py_self_, PLib::Point_nD<double,2>* p0, const int p1):
//         PLib::BasicArray<PLib::Point_nD<double, 2> >(p0, p1), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_Point_nD_double_2_Wrapper(PyObject* py_self_, BasicList<PLib::Point_nD<double, 2> >& p0):
//         PLib::BasicArray<PLib::Point_nD<double, 2> >(p0), py_self(py_self_) {}
// 
//     void reset(const PLib::Point_nD<double,2> p0) {
//         call_method< void >(py_self, "reset", p0);
//     }
// 
//     void default_reset_0() {
//         PLib::BasicArray<PLib::Point_nD<double, 2> >::reset();
//     }
// 
//     void default_reset_1(const PLib::Point_nD<double,2> p0) {
//         PLib::BasicArray<PLib::Point_nD<double, 2> >::reset(p0);
//     }
// 
//     PyObject* py_self;
// };

// BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_BasicArray_PLib_Point_nD_double_2_push_back_overloads_1_3, push_back, 1, 3)

// struct PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper: PLib::BasicArray<PLib::HPoint_nD<double, 3> >
// {
//     PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper(PyObject* py_self_):
//         PLib::BasicArray<PLib::HPoint_nD<double, 3> >(), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper(PyObject* py_self_, const int p0):
//         PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::HPoint_nD<double, 3> >& p0):
//         PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper(PyObject* py_self_, PLib::HPoint_nD<double,3>* p0, const int p1):
//         PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0, p1), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper(PyObject* py_self_, BasicList<PLib::HPoint_nD<double, 3> >& p0):
//         PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0), py_self(py_self_) {}
// 
//     void reset(const PLib::HPoint_nD<double,3> p0) {
//         call_method< void >(py_self, "reset", p0);
//     }
// 
//     void default_reset_0() {
//         PLib::BasicArray<PLib::HPoint_nD<double, 3> >::reset();
//     }
// 
//     void default_reset_1(const PLib::HPoint_nD<double,3> p0) {
//         PLib::BasicArray<PLib::HPoint_nD<double, 3> >::reset(p0);
//     }
// 
//     PyObject* py_self;
// };
// 
// BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_BasicArray_PLib_HPoint_nD_double_3_push_back_overloads_1_3, push_back, 1, 3)
// 
// struct PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper: PLib::BasicArray<PLib::HPoint_nD<double, 2> >
// {
//     PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper(PyObject* py_self_):
//         PLib::BasicArray<PLib::HPoint_nD<double, 2> >(), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper(PyObject* py_self_, const int p0):
//         PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::HPoint_nD<double, 2> >& p0):
//         PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper(PyObject* py_self_, PLib::HPoint_nD<double,2>* p0, const int p1):
//         PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0, p1), py_self(py_self_) {}
// 
//     PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper(PyObject* py_self_, BasicList<PLib::HPoint_nD<double, 2> >& p0):
//         PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0), py_self(py_self_) {}
// 
//     void reset(const PLib::HPoint_nD<double,2> p0) {
//         call_method< void >(py_self, "reset", p0);
//     }
// 
//     void default_reset_0() {
//         PLib::BasicArray<PLib::HPoint_nD<double, 2> >::reset();
//     }
// 
//     void default_reset_1(const PLib::HPoint_nD<double,2> p0) {
//         PLib::BasicArray<PLib::HPoint_nD<double, 2> >::reset(p0);
//     }
// 
//     PyObject* py_self;
// };
// 
// BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(PLib_BasicArray_PLib_HPoint_nD_double_2_push_back_overloads_1_3, push_back, 1, 3)

}// namespace 


// Module ======================================================================
BOOST_PYTHON_MODULE(NurbsMatrixD)
{
    class_< PLib::Basic2DArray<PLib::Point_nD<double, 3> > >("Array2D_Point3Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Basic2DArray<PLib::Point_nD<double, 3> >& >())
        .def(init< PLib::Point_nD<double,3>*, const int, const int >())
        .def("rows", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::rows)
        .def("cols", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::cols)
        .def("resize", (void (PLib::Basic2DArray<PLib::Point_nD<double, 3> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 3> >::resize)
        .def("resize", (void (PLib::Basic2DArray<PLib::Point_nD<double, 3> >::*)(const PLib::Basic2DArray<PLib::Point_nD<double, 3> >&) )&PLib::Basic2DArray<PLib::Point_nD<double, 3> >::resize)
        .def("resizeKeep", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::resizeKeep)
        .def("reset", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::reset, PLib_Basic2DArray_PLib_Point_nD_double_3_reset_overloads_0_1())
        .def("io_elem_width", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::io_elem_width)
        .def("io_by_rows", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::io_by_rows)
        .def("io_by_columns", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::io_by_columns)
//         .def("print", &PLib::Basic2DArray<PLib::Point_nD<double, 3> >::print)
//         .def("elem", (PLib::Point_nD<double,3>& (PLib::Basic2DArray<PLib::Point_nD<double, 3> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 3> >::elem)
        .def("elem", (PLib::Point_nD<double,3> (PLib::Basic2DArray<PLib::Point_nD<double, 3> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::Point_nD<double, 3> >::elem)
//         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
        .def(self_ns::str(self))
//         .def("__call__", (PLib::Point_nD<double,3>& (PLib::Basic2DArray<PLib::Point_nD<double, 3> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 3> >::operator ())
        .def("__call__", (PLib::Point_nD<double,3> (PLib::Basic2DArray<PLib::Point_nD<double, 3> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::Point_nD<double, 3> >::operator ())
    ;

    class_< PLib::Basic2DArray<PLib::Point_nD<double, 2> > >("Array2D_Point2Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Basic2DArray<PLib::Point_nD<double, 2> >& >())
        .def(init< PLib::Point_nD<double,2>*, const int, const int >())
        .def("rows", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::rows)
        .def("cols", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::cols)
        .def("resize", (void (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::resize)
        .def("resize", (void (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const PLib::Basic2DArray<PLib::Point_nD<double, 2> >&) )&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::resize)
        .def("resizeKeep", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::resizeKeep)
        .def("reset", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::reset, PLib_Basic2DArray_PLib_Point_nD_double_2_reset_overloads_0_1())
        .def("io_elem_width", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::io_elem_width)
        .def("io_by_rows", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::io_by_rows)
        .def("io_by_columns", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::io_by_columns)
//         .def("print", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::print)
//         .def("elem", (PLib::Point_nD<double,2>& (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::elem)
        .def("elem", (PLib::Point_nD<double,2> (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::elem)
//         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
        .def(self_ns::str(self))
//         .def("__call__", (PLib::Point_nD<double,2>& (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::operator ())
        .def("__call__", (PLib::Point_nD<double,2> (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::operator ())
    ;

    class_< PLib::Basic2DArray<PLib::HPoint_nD<double, 3> > >("Array2D_HPoint3Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >& >())
        .def(init< PLib::HPoint_nD<double,3>*, const int, const int >())
        .def("rows", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::rows)
        .def("cols", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::cols)
        .def("resize", (void (PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::resize)
        .def("resize", (void (PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::*)(const PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >&) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::resize)
        .def("resizeKeep", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::resizeKeep)
        .def("reset", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::reset, PLib_Basic2DArray_PLib_HPoint_nD_double_3_reset_overloads_0_1())
        .def("io_elem_width", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::io_elem_width)
        .def("io_by_rows", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::io_by_rows)
        .def("io_by_columns", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::io_by_columns)
//         .def("print", &PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::print)
//         .def("elem", (PLib::HPoint_nD<double,3>& (PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::elem)
        .def("elem", (PLib::HPoint_nD<double,3> (PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::elem)
//         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
        .def(self_ns::str(self))
//         .def("__call__", (PLib::HPoint_nD<double,3>& (PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::operator ())
        .def("__call__", (PLib::HPoint_nD<double,3> (PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::HPoint_nD<double, 3> >::operator ())
    ;

    class_< PLib::Basic2DArray<PLib::HPoint_nD<double, 2> > >("Array2D_HPoint2Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >& >())
        .def(init< PLib::HPoint_nD<double,2>*, const int, const int >())
        .def("rows", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::rows)
        .def("cols", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::cols)
        .def("resize", (void (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("resize", (void (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >&) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("resizeKeep", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::resizeKeep)
        .def("reset", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::reset, PLib_Basic2DArray_PLib_HPoint_nD_double_2_reset_overloads_0_1())
        .def("io_elem_width", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::io_elem_width)
        .def("io_by_rows", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::io_by_rows)
        .def("io_by_columns", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::io_by_columns)
//         .def("print", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::print)
//         .def("elem", (PLib::HPoint_nD<double,2>& (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::elem)
        .def("elem", (PLib::HPoint_nD<double,2> (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::elem)
//         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
        .def(self_ns::str(self))
//         .def("__call__", (PLib::HPoint_nD<double,2>& (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::operator ())
        .def("__call__", (PLib::HPoint_nD<double,2> (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::operator ())
    ;

//     class_< PLib::BasicArray<PLib::Point_nD<double, 3> >, PLib_BasicArray_PLib_Point_nD_double_3_Wrapper >("PLib_BasicArray_PLib_Point_nD_double_3", init<  >())
//         .def(init< const int >())
//         .def(init< const PLib::BasicArray<PLib::Point_nD<double, 3> >& >())
//         .def(init< PLib::Point_nD<double,3>*, const int >())
//         .def(init< BasicList<PLib::Point_nD<double, 3> >& >())
//         .def("reset", &PLib::BasicArray<PLib::Point_nD<double, 3> >::reset, &PLib_BasicArray_PLib_Point_nD_double_3_Wrapper::default_reset_1)
//         .def("reset", &PLib_BasicArray_PLib_Point_nD_double_3_Wrapper::default_reset_0)
//         .def("n", &PLib::BasicArray<PLib::Point_nD<double, 3> >::n)
//         .def("size", &PLib::BasicArray<PLib::Point_nD<double, 3> >::size)
//         .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)(const int) )&PLib::BasicArray<PLib::Point_nD<double, 3> >::resize)
//         .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)(const PLib::BasicArray<PLib::Point_nD<double, 3> >&) )&PLib::BasicArray<PLib::Point_nD<double, 3> >::resize)
//         .def("trim", &PLib::BasicArray<PLib::Point_nD<double, 3> >::trim)
//         .def("clear", &PLib::BasicArray<PLib::Point_nD<double, 3> >::clear)
//         .def("untrim", &PLib::BasicArray<PLib::Point_nD<double, 3> >::untrim)
// //         .def("push_back", &PLib::BasicArray<PLib::Point_nD<double, 3> >::push_back, PLib_BasicArray_PLib_Point_nD_double_3_push_back_overloads_1_3())
// //         .def("memory", &PLib::BasicArray<PLib::Point_nD<double, 3> >::memory)
//         .def("width", &PLib::BasicArray<PLib::Point_nD<double, 3> >::width)
// //         .def("print", &PLib::BasicArray<PLib::Point_nD<double, 3> >::print)
// //         .def("begin", (PLib::Point_nD<double,3>* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 3> >::begin)
// //         .def("begin", (const PLib::Point_nD<double,3>* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 3> >::begin)
// //         .def("end", (PLib::Point_nD<double,3>* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 3> >::end)
// //         .def("end", (const PLib::Point_nD<double,3>* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 3> >::end)
// //         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
//         .def(self_ns::str(self))
//         .def( self != self )
//         .def( self == self )
//     ;

//     class_< PLib::BasicArray<PLib::Point_nD<double, 2> >, PLib_BasicArray_PLib_Point_nD_double_2_Wrapper >("PLib_BasicArray_PLib_Point_nD_double_2", init<  >())
//         .def(init< const int >())
//         .def(init< const PLib::BasicArray<PLib::Point_nD<double, 2> >& >())
//         .def(init< PLib::Point_nD<double,2>*, const int >())
//         .def(init< BasicList<PLib::Point_nD<double, 2> >& >())
//         .def("reset", &PLib::BasicArray<PLib::Point_nD<double, 2> >::reset, &PLib_BasicArray_PLib_Point_nD_double_2_Wrapper::default_reset_1)
//         .def("reset", &PLib_BasicArray_PLib_Point_nD_double_2_Wrapper::default_reset_0)
//         .def("n", &PLib::BasicArray<PLib::Point_nD<double, 2> >::n)
//         .def("size", &PLib::BasicArray<PLib::Point_nD<double, 2> >::size)
//         .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)(const int) )&PLib::BasicArray<PLib::Point_nD<double, 2> >::resize)
//         .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)(const PLib::BasicArray<PLib::Point_nD<double, 2> >&) )&PLib::BasicArray<PLib::Point_nD<double, 2> >::resize)
//         .def("trim", &PLib::BasicArray<PLib::Point_nD<double, 2> >::trim)
//         .def("clear", &PLib::BasicArray<PLib::Point_nD<double, 2> >::clear)
//         .def("untrim", &PLib::BasicArray<PLib::Point_nD<double, 2> >::untrim)
// //         .def("push_back", &PLib::BasicArray<PLib::Point_nD<double, 2> >::push_back, PLib_BasicArray_PLib_Point_nD_double_2_push_back_overloads_1_3())
// //         .def("memory", &PLib::BasicArray<PLib::Point_nD<double, 2> >::memory)
//         .def("width", &PLib::BasicArray<PLib::Point_nD<double, 2> >::width)
// //         .def("print", &PLib::BasicArray<PLib::Point_nD<double, 2> >::print)
// //         .def("begin", (PLib::Point_nD<double,2>* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 2> >::begin)
// //         .def("begin", (const PLib::Point_nD<double,2>* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 2> >::begin)
// //         .def("end", (PLib::Point_nD<double,2>* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 2> >::end)
// //         .def("end", (const PLib::Point_nD<double,2>* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 2> >::end)
//         .def(self_ns::str(self))
//         .def( self == self )
// //         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
//         .def( self != self )
//     ;
/*
    class_< PLib::BasicArray<PLib::HPoint_nD<double, 3> >, PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper >("PLib_BasicArray_PLib_HPoint_nD_double_3", init<  >())
        .def(init< const int >())
        .def(init< const PLib::BasicArray<PLib::HPoint_nD<double, 3> >& >())
        .def(init< PLib::HPoint_nD<double,3>*, const int >())
        .def(init< BasicList<PLib::HPoint_nD<double, 3> >& >())
        .def("reset", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::reset, &PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper::default_reset_1)
        .def("reset", &PLib_BasicArray_PLib_HPoint_nD_double_3_Wrapper::default_reset_0)
        .def("n", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::n)
        .def("size", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::size)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)(const int) )&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::resize)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)(const PLib::BasicArray<PLib::HPoint_nD<double, 3> >&) )&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::resize)
        .def("trim", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::trim)
        .def("clear", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::clear)
        .def("untrim", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::untrim)
//         .def("push_back", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::push_back, PLib_BasicArray_PLib_HPoint_nD_double_3_push_back_overloads_1_3())
//         .def("memory", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::memory)
        .def("width", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::width)
//         .def("print", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::print)
//         .def("begin", (PLib::HPoint_nD<double,3>* (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)() )&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::begin)
//         .def("begin", (const PLib::HPoint_nD<double,3>* (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)() const)&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::begin)
//         .def("end", (PLib::HPoint_nD<double,3>* (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)() )&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::end)
//         .def("end", (const PLib::HPoint_nD<double,3>* (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)() const)&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::end)
        .def(self_ns::str(self))
        .def( self == self )
//         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
        .def( self != self )
    ;

    class_< PLib::BasicArray<PLib::HPoint_nD<double, 2> >, PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper >("PLib_BasicArray_PLib_HPoint_nD_double_2", init<  >())
        .def(init< const int >())
        .def(init< const PLib::BasicArray<PLib::HPoint_nD<double, 2> >& >())
        .def(init< PLib::HPoint_nD<double,2>*, const int >())
        .def(init< BasicList<PLib::HPoint_nD<double, 2> >& >())
        .def("reset", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::reset, &PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper::default_reset_1)
        .def("reset", &PLib_BasicArray_PLib_HPoint_nD_double_2_Wrapper::default_reset_0)
        .def("n", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::n)
        .def("size", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::size)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)(const int) )&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)(const PLib::BasicArray<PLib::HPoint_nD<double, 2> >&) )&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("trim", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::trim)
        .def("clear", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::clear)
        .def("untrim", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::untrim)
//         .def("push_back", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::push_back, PLib_BasicArray_PLib_HPoint_nD_double_2_push_back_overloads_1_3())
//         .def("memory", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::memory)
        .def("width", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::width)
//         .def("print", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::print)
//         .def("begin", (PLib::HPoint_nD<double,2>* (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)() )&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::begin)
//         .def("begin", (const PLib::HPoint_nD<double,2>* (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)() const)&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::begin)
//         .def("end", (PLib::HPoint_nD<double,2>* (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)() )&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::end)
//         .def("end", (const PLib::HPoint_nD<double,2>* (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)() const)&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::end)
        .def(self_ns::str(self))
        .def( self == self )
//         .def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
        .def( self != self )
    ;*/

    class_< PLib::Matrix<PLib::Point_nD<double, 2> > >("Matrix_Point2Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Matrix<PLib::Point_nD<double, 2> >& >())
        .def(init< PLib::Point_nD<double,2>*, const int, const int >())
        .def("submatrix", &PLib::Matrix<PLib::Point_nD<double, 2> >::submatrix)
        .def("as", &PLib::Matrix<PLib::Point_nD<double, 2> >::as)
        .def("get", &PLib::Matrix<PLib::Point_nD<double, 2> >::get)
        .def("herm", &PLib::Matrix<PLib::Point_nD<double, 2> >::herm)
        .def("transpose", &PLib::Matrix<PLib::Point_nD<double, 2> >::transpose)
        .def("flop", &PLib::Matrix<PLib::Point_nD<double, 2> >::flop)
        .def("trace", &PLib::Matrix<PLib::Point_nD<double, 2> >::trace)
        .def("norm", &PLib::Matrix<PLib::Point_nD<double, 2> >::norm)
        .def("diag", &PLib::Matrix<PLib::Point_nD<double, 2> >::diag)
        .def("getDiag", &PLib::Matrix<PLib::Point_nD<double, 2> >::getDiag)
        .def("qSort", &PLib::Matrix<PLib::Point_nD<double, 2> >::qSort)
        .def("read", (int (PLib::Matrix<PLib::Point_nD<double, 2> >::*)(char*) )&PLib::Matrix<PLib::Point_nD<double, 2> >::read)
        .def("read", (int (PLib::Matrix<PLib::Point_nD<double, 2> >::*)(char*, int, int) )&PLib::Matrix<PLib::Point_nD<double, 2> >::read)
        .def("write", &PLib::Matrix<PLib::Point_nD<double, 2> >::write)
        .def("writeRaw", &PLib::Matrix<PLib::Point_nD<double, 2> >::writeRaw)
        .def("rows", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::rows)
        .def("cols", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::cols)
        .def("resize", (void (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::resize)
        .def("resize", (void (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const PLib::Basic2DArray<PLib::Point_nD<double, 2> >&) )&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::resize)
        .def("resizeKeep", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::resizeKeep)
        .def("reset", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::reset, PLib_Basic2DArray_PLib_Point_nD_double_2_reset_overloads_0_1())
        .def("io_elem_width", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::io_elem_width)
        .def("io_by_rows", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::io_by_rows)
        .def("io_by_columns", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::io_by_columns)
//         .def("print", &PLib::Basic2DArray<PLib::Point_nD<double, 2> >::print)
//         .def("elem", (PLib::Point_nD<double,2>& (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::elem)
        .def("elem", (PLib::Point_nD<double,2> (PLib::Basic2DArray<PLib::Point_nD<double, 2> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::Point_nD<double, 2> >::elem)
        .def( self * self )
        .def( other< double >() * self )
        .def( self == self )
        .def( self + self )
//         .def( other< std::complex<double> >() * self )
//         .def( self * other< PLib::Vector<PLib::Point_nD<double, 2> > >() )
        .def( self - self )
//         .def( self != self )
        .def( self += self )
        .def( self -= self )
        .def( self += other< double >() )
        .def( self -= other< double >() )
        .def( self *= other< double >() )
        .def( self /= other< double >() )
    ;

    class_< PLib::Matrix<PLib::Point_nD<double, 3> >, bases< PLib::Basic2DArray<PLib::Point_nD<double, 3> > >  >("Matrix_Point3Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Matrix<PLib::Point_nD<double, 3> >& >())
        .def(init< PLib::Point_nD<double,3>*, const int, const int >())
        .def("submatrix", &PLib::Matrix<PLib::Point_nD<double, 3> >::submatrix)
        .def("as", &PLib::Matrix<PLib::Point_nD<double, 3> >::as)
        .def("get", &PLib::Matrix<PLib::Point_nD<double, 3> >::get)
        .def("herm", &PLib::Matrix<PLib::Point_nD<double, 3> >::herm)
        .def("transpose", &PLib::Matrix<PLib::Point_nD<double, 3> >::transpose)
        .def("flop", &PLib::Matrix<PLib::Point_nD<double, 3> >::flop)
        .def("trace", &PLib::Matrix<PLib::Point_nD<double, 3> >::trace)
        .def("norm", &PLib::Matrix<PLib::Point_nD<double, 3> >::norm)
        .def("diag", &PLib::Matrix<PLib::Point_nD<double, 3> >::diag)
        .def("getDiag", &PLib::Matrix<PLib::Point_nD<double, 3> >::getDiag)
        .def("qSort", &PLib::Matrix<PLib::Point_nD<double, 3> >::qSort)
        .def("read", (int (PLib::Matrix<PLib::Point_nD<double, 3> >::*)(char*) )&PLib::Matrix<PLib::Point_nD<double, 3> >::read)
        .def("read", (int (PLib::Matrix<PLib::Point_nD<double, 3> >::*)(char*, int, int) )&PLib::Matrix<PLib::Point_nD<double, 3> >::read)
        .def("write", &PLib::Matrix<PLib::Point_nD<double, 3> >::write)
        .def("writeRaw", &PLib::Matrix<PLib::Point_nD<double, 3> >::writeRaw)
        .def( self * self )
        .def( other< double >() * self )
        .def( self == self )
        .def( self + self )
//         .def( other< std::complex<double> >() * self )
//         .def( self * other< PLib::Vector<PLib::Point_nD<double, 3> > >() )
        .def( self - self )
//         .def( self != self )
        .def( self += self )
        .def( self -= self )
        .def( self += other< double >() )
        .def( self -= other< double >() )
        .def( self *= other< double >() )
        .def( self /= other< double >() )
    ;

    class_< PLib::Matrix<PLib::HPoint_nD<double, 2> > >("Matrix_HPoint2Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Matrix<PLib::HPoint_nD<double, 2> >& >())
        .def(init< PLib::HPoint_nD<double,2>*, const int, const int >())
        .def("submatrix", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::submatrix)
        .def("as", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::as)
        .def("get", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::get)
        .def("herm", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::herm)
        .def("transpose", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::transpose)
        .def("flop", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::flop)
        .def("trace", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::trace)
        .def("norm", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::norm)
        .def("diag", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::diag)
        .def("getDiag", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::getDiag)
        .def("qSort", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::qSort)
        .def("read", (int (PLib::Matrix<PLib::HPoint_nD<double, 2> >::*)(char*) )&PLib::Matrix<PLib::HPoint_nD<double, 2> >::read)
        .def("read", (int (PLib::Matrix<PLib::HPoint_nD<double, 2> >::*)(char*, int, int) )&PLib::Matrix<PLib::HPoint_nD<double, 2> >::read)
        .def("write", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::write)
        .def("writeRaw", &PLib::Matrix<PLib::HPoint_nD<double, 2> >::writeRaw)
        .def("rows", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::rows)
        .def("cols", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::cols)
        .def("resize", (void (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("resize", (void (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >&) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("resizeKeep", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::resizeKeep)
        .def("reset", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::reset, PLib_Basic2DArray_PLib_HPoint_nD_double_2_reset_overloads_0_1())
        .def("io_elem_width", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::io_elem_width)
        .def("io_by_rows", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::io_by_rows)
        .def("io_by_columns", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::io_by_columns)
//         .def("print", &PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::print)
//         .def("elem", (PLib::HPoint_nD<double,2>& (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) )&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::elem)
        .def("elem", (PLib::HPoint_nD<double,2> (PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::*)(const int, const int) const)&PLib::Basic2DArray<PLib::HPoint_nD<double, 2> >::elem)
        .def( self * self )
        .def( other< double >() * self )
//         .def( self != self )
        .def( self == self )
        .def( self + self )
//         .def( other< std::complex<double> >() * self )
//         .def( self * other< PLib::Vector<PLib::HPoint_nD<double, 2> > >() )
        .def( self - self )
        .def( self += self )
        .def( self -= self )
        .def( self += other< double >() )
        .def( self -= other< double >() )
        .def( self *= other< double >() )
        .def( self /= other< double >() )
    ;

    class_< PLib::Matrix<PLib::HPoint_nD<double, 3> >, bases< PLib::Basic2DArray<PLib::HPoint_nD<double, 3> > >  >("Matrix_HPoint3Dd", init<  >())
        .def(init< const int, const int >())
        .def(init< const PLib::Matrix<PLib::HPoint_nD<double, 3> >& >())
        .def(init< PLib::HPoint_nD<double,3>*, const int, const int >())
        .def("submatrix", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::submatrix)
        .def("as", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::as)
        .def("get", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::get)
        .def("herm", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::herm)
        .def("transpose", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::transpose)
        .def("flop", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::flop)
        .def("trace", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::trace)
        .def("norm", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::norm)
        .def("diag", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::diag)
        .def("getDiag", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::getDiag)
        .def("qSort", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::qSort)
        .def("read", (int (PLib::Matrix<PLib::HPoint_nD<double, 3> >::*)(char*) )&PLib::Matrix<PLib::HPoint_nD<double, 3> >::read)
        .def("read", (int (PLib::Matrix<PLib::HPoint_nD<double, 3> >::*)(char*, int, int) )&PLib::Matrix<PLib::HPoint_nD<double, 3> >::read)
        .def("write", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::write)
        .def("writeRaw", &PLib::Matrix<PLib::HPoint_nD<double, 3> >::writeRaw)
        .def( self * self )
//         .def( self != self )
        .def( self == self )
        .def( self + self )
        .def( other< double >() * self )
//         .def( other< std::complex<double> >() * self )
//         .def( self * other< PLib::Vector<PLib::HPoint_nD<double, 3> > >() )
        .def( self - self )
        .def( self += self )
        .def( self -= self )
        .def( self += other< double >() )
        .def( self -= other< double >() )
        .def( self *= other< double >() )
        .def( self /= other< double >() )
    ;

}

