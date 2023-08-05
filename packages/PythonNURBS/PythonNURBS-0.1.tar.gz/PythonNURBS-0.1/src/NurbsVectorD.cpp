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
#include <nurbs++/vector.h>

// Using =======================================================================
using namespace boost::python;

// Declarations ================================================================
namespace  {

struct BasicArray_Point3Dd_Wrapper: PLib::BasicArray<PLib::Point_nD<double, 3> >
{
    BasicArray_Point3Dd_Wrapper(PyObject* py_self_):
        PLib::BasicArray<PLib::Point_nD<double, 3> >(), py_self(py_self_) {}

    BasicArray_Point3Dd_Wrapper(PyObject* py_self_, const int p0):
        PLib::BasicArray<PLib::Point_nD<double, 3> >(p0), py_self(py_self_) {}

    BasicArray_Point3Dd_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::Point_nD<double, 3> >& p0):
        PLib::BasicArray<PLib::Point_nD<double, 3> >(p0), py_self(py_self_) {}

    BasicArray_Point3Dd_Wrapper(PyObject* py_self_, PLib::Point3Dd* p0, const int p1):
        PLib::BasicArray<PLib::Point_nD<double, 3> >(p0, p1), py_self(py_self_) {}

    BasicArray_Point3Dd_Wrapper(PyObject* py_self_, BasicList<PLib::Point_nD<double, 3> >& p0):
        PLib::BasicArray<PLib::Point_nD<double, 3> >(p0), py_self(py_self_) {}

    void reset(const PLib::Point3Dd p0) {
        call_method< void >(py_self, "reset", p0);
    }

    void default_reset_0() {
        PLib::BasicArray<PLib::Point_nD<double, 3> >::reset();
    }

    void default_reset_1(const PLib::Point3Dd p0) {
        PLib::BasicArray<PLib::Point_nD<double, 3> >::reset(p0);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(BasicArray_Point3Dd_push_back_overloads_1_3, push_back, 1, 3)

struct BasicArray_Point2Dd_Wrapper: PLib::BasicArray<PLib::Point_nD<double, 2> >
{
    BasicArray_Point2Dd_Wrapper(PyObject* py_self_):
        PLib::BasicArray<PLib::Point_nD<double, 2> >(), py_self(py_self_) {}

    BasicArray_Point2Dd_Wrapper(PyObject* py_self_, const int p0):
        PLib::BasicArray<PLib::Point_nD<double, 2> >(p0), py_self(py_self_) {}

    BasicArray_Point2Dd_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::Point_nD<double, 2> >& p0):
        PLib::BasicArray<PLib::Point_nD<double, 2> >(p0), py_self(py_self_) {}

    BasicArray_Point2Dd_Wrapper(PyObject* py_self_, PLib::Point2Dd* p0, const int p1):
        PLib::BasicArray<PLib::Point_nD<double, 2> >(p0, p1), py_self(py_self_) {}

    BasicArray_Point2Dd_Wrapper(PyObject* py_self_, BasicList<PLib::Point_nD<double, 2> >& p0):
        PLib::BasicArray<PLib::Point_nD<double, 2> >(p0), py_self(py_self_) {}

    void reset(const PLib::Point2Dd p0) {
        call_method< void >(py_self, "reset", p0);
    }

    void default_reset_0() {
        PLib::BasicArray<PLib::Point_nD<double, 2> >::reset();
    }

    void default_reset_1(const PLib::Point2Dd p0) {
        PLib::BasicArray<PLib::Point_nD<double, 2> >::reset(p0);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(BasicArray_Point2Dd_push_back_overloads_1_3, push_back, 1, 3)

struct BasicArray_HPoint3Dd_Wrapper: PLib::BasicArray<PLib::HPoint_nD<double, 3> >
{
    BasicArray_HPoint3Dd_Wrapper(PyObject* py_self_):
        PLib::BasicArray<PLib::HPoint_nD<double, 3> >(), py_self(py_self_) {}

    BasicArray_HPoint3Dd_Wrapper(PyObject* py_self_, const int p0):
        PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0), py_self(py_self_) {}

    BasicArray_HPoint3Dd_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::HPoint_nD<double, 3> >& p0):
        PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0), py_self(py_self_) {}

    BasicArray_HPoint3Dd_Wrapper(PyObject* py_self_, PLib::HPoint_nD<double,3>* p0, const int p1):
        PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0, p1), py_self(py_self_) {}

    BasicArray_HPoint3Dd_Wrapper(PyObject* py_self_, BasicList<PLib::HPoint_nD<double, 3> >& p0):
        PLib::BasicArray<PLib::HPoint_nD<double, 3> >(p0), py_self(py_self_) {}

    void reset(const PLib::HPoint_nD<double,3> p0) {
        call_method< void >(py_self, "reset", p0);
    }

    void default_reset_0() {
        PLib::BasicArray<PLib::HPoint_nD<double, 3> >::reset();
    }

    void default_reset_1(const PLib::HPoint_nD<double,3> p0) {
        PLib::BasicArray<PLib::HPoint_nD<double, 3> >::reset(p0);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(BasicArray_HPoint3Dd_push_back_overloads_1_3, push_back, 1, 3)

struct BasicArray_HPoint2Dd_Wrapper: PLib::BasicArray<PLib::HPoint_nD<double, 2> >
{
    BasicArray_HPoint2Dd_Wrapper(PyObject* py_self_):
        PLib::BasicArray<PLib::HPoint_nD<double, 2> >(), py_self(py_self_) {}

    BasicArray_HPoint2Dd_Wrapper(PyObject* py_self_, const int p0):
        PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0), py_self(py_self_) {}

    BasicArray_HPoint2Dd_Wrapper(PyObject* py_self_, const PLib::BasicArray<PLib::HPoint_nD<double, 2> >& p0):
        PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0), py_self(py_self_) {}

    BasicArray_HPoint2Dd_Wrapper(PyObject* py_self_, PLib::HPoint_nD<double,2>* p0, const int p1):
        PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0, p1), py_self(py_self_) {}

    BasicArray_HPoint2Dd_Wrapper(PyObject* py_self_, BasicList<PLib::HPoint_nD<double, 2> >& p0):
        PLib::BasicArray<PLib::HPoint_nD<double, 2> >(p0), py_self(py_self_) {}

    void reset(const PLib::HPoint_nD<double,2> p0) {
        call_method< void >(py_self, "reset", p0);
    }

    void default_reset_0() {
        PLib::BasicArray<PLib::HPoint_nD<double, 2> >::reset();
    }

    void default_reset_1(const PLib::HPoint_nD<double,2> p0) {
        PLib::BasicArray<PLib::HPoint_nD<double, 2> >::reset(p0);
    }

    PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(BasicArray_HPoint2Dd_push_back_overloads_1_3, push_back, 1, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_Point3Dd_qSort_overloads_0_1, qSort, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_Point3Dd_sortIndex_overloads_1_2, sortIndex, 1, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_Point2Dd_qSort_overloads_0_1, qSort, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_Point2Dd_sortIndex_overloads_1_2, sortIndex, 1, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_HPoint3Dd_qSort_overloads_0_1, qSort, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_HPoint3Dd_sortIndex_overloads_1_2, sortIndex, 1, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_HPoint2Dd_qSort_overloads_0_1, qSort, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(Vector_HPoint2Dd_sortIndex_overloads_1_2, sortIndex, 1, 2)

}// namespace 


// Module ======================================================================
BOOST_PYTHON_MODULE(NurbsVectorD)
{
    scope* BasicList_Point3Dd_scope = new scope(
    class_< BasicList<PLib::Point_nD<double, 3> >, boost::noncopyable >("BasicList_Point3Dd", init<  >())
        .def(init< BasicList<PLib::Point_nD<double, 3> >& >())
        .def_readwrite("current", &BasicList<PLib::Point_nD<double, 3> >::current)
        .def_readwrite("data", &BasicNode<PLib::Point_nD<double, 3> >::data)
        .def_readwrite("prev", &BasicNode<PLib::Point_nD<double, 3> >::prev)
        .def_readwrite("next", &BasicNode<PLib::Point_nD<double, 3> >::next)
        //.def("first", &BasicList<PLib::Point_nD<double, 3> >::first)
        //.def("last", &BasicList<PLib::Point_nD<double, 3> >::last)
        .def("reset", &BasicList<PLib::Point_nD<double, 3> >::reset)
        .def("add", (void (BasicList<PLib::Point_nD<double, 3> >::*)(BasicNode<PLib::Point_nD<double, 3> >*) )&BasicList<PLib::Point_nD<double, 3> >::add)
        .def("add", (void (BasicList<PLib::Point_nD<double, 3> >::*)(const PLib::Point_nD<double,3>&) )&BasicList<PLib::Point_nD<double, 3> >::add)
        .def("addElements", &BasicList<PLib::Point_nD<double, 3> >::addElements)
        //.def("remove", &BasicList<PLib::Point_nD<double, 3> >::remove)
        .def("erase", &BasicList<PLib::Point_nD<double, 3> >::erase)
        //.def("goToFirst", &BasicList<PLib::Point_nD<double, 3> >::goToFirst)
        //.def("goToNext", &BasicList<PLib::Point_nD<double, 3> >::goToNext)
        //.def("goToPrevious", &BasicList<PLib::Point_nD<double, 3> >::goToPrevious)
        .def("size", &BasicList<PLib::Point_nD<double, 3> >::size)
        .def("resetMode", &BasicList<PLib::Point_nD<double, 3> >::resetMode)
        .def("setResetMode", &BasicList<PLib::Point_nD<double, 3> >::setResetMode)
    );

    enum_< BasicList<PLib::Point_nD<double, 3> >::ListResetMode >("ListResetMode")
        .value("delete_at_reset", BasicList<PLib::Point_nD<double, 3> >::delete_at_reset)
        .value("keep_at_reset", BasicList<PLib::Point_nD<double, 3> >::keep_at_reset)
    ;

    delete BasicList_Point3Dd_scope;

    scope* BasicList_Point2Dd_scope = new scope(
    class_< BasicList<PLib::Point_nD<double, 2> >, boost::noncopyable >("BasicList_Point2Dd", init<  >())
        .def(init< BasicList<PLib::Point_nD<double, 2> >& >())
        .def_readwrite("current", &BasicList<PLib::Point_nD<double, 2> >::current)
        .def_readwrite("data", &BasicNode<PLib::Point_nD<double, 2> >::data)
        .def_readwrite("prev", &BasicNode<PLib::Point_nD<double, 2> >::prev)
        .def_readwrite("next", &BasicNode<PLib::Point_nD<double, 2> >::next)
        //.def("first", &BasicList<PLib::Point_nD<double, 2> >::first)
        //.def("last", &BasicList<PLib::Point_nD<double, 2> >::last)
        .def("reset", &BasicList<PLib::Point_nD<double, 2> >::reset)
        .def("add", (void (BasicList<PLib::Point_nD<double, 2> >::*)(BasicNode<PLib::Point_nD<double, 2> >*) )&BasicList<PLib::Point_nD<double, 2> >::add)
        .def("add", (void (BasicList<PLib::Point_nD<double, 2> >::*)(const PLib::Point_nD<double,2>&) )&BasicList<PLib::Point_nD<double, 2> >::add)
        .def("addElements", &BasicList<PLib::Point_nD<double, 2> >::addElements)
        //.def("remove", &BasicList<PLib::Point_nD<double, 2> >::remove)
        .def("erase", &BasicList<PLib::Point_nD<double, 2> >::erase)
        //.def("goToFirst", &BasicList<PLib::Point_nD<double, 2> >::goToFirst)
        //.def("goToNext", &BasicList<PLib::Point_nD<double, 2> >::goToNext)
        //.def("goToPrevious", &BasicList<PLib::Point_nD<double, 2> >::goToPrevious)
        .def("size", &BasicList<PLib::Point_nD<double, 2> >::size)
        .def("resetMode", &BasicList<PLib::Point_nD<double, 2> >::resetMode)
        .def("setResetMode", &BasicList<PLib::Point_nD<double, 2> >::setResetMode)
    );

    enum_< BasicList<PLib::Point_nD<double, 2> >::ListResetMode >("ListResetMode")
        .value("delete_at_reset", BasicList<PLib::Point_nD<double, 2> >::delete_at_reset)
        .value("keep_at_reset", BasicList<PLib::Point_nD<double, 2> >::keep_at_reset)
    ;

    delete BasicList_Point2Dd_scope;

    scope* BasicList_HPoint3Dd_scope = new scope(
    class_< BasicList<PLib::HPoint_nD<double, 3> >, boost::noncopyable >("BasicList_HPoint3Dd", init<  >())
        .def(init< BasicList<PLib::HPoint_nD<double, 3> >& >())
        .def_readwrite("current", &BasicList<PLib::HPoint_nD<double, 3> >::current)
        .def_readwrite("data", &BasicNode<PLib::HPoint_nD<double, 3> >::data)
        .def_readwrite("prev", &BasicNode<PLib::HPoint_nD<double, 3> >::prev)
        .def_readwrite("next", &BasicNode<PLib::HPoint_nD<double, 3> >::next)
        //.def("first", &BasicList<PLib::HPoint_nD<double, 3> >::first)
        //.def("last", &BasicList<PLib::HPoint_nD<double, 3> >::last)
        .def("reset", &BasicList<PLib::HPoint_nD<double, 3> >::reset)
        .def("add", (void (BasicList<PLib::HPoint_nD<double, 3> >::*)(BasicNode<PLib::HPoint_nD<double, 3> >*) )&BasicList<PLib::HPoint_nD<double, 3> >::add)
        .def("add", (void (BasicList<PLib::HPoint_nD<double, 3> >::*)(const PLib::HPoint_nD<double,3>&) )&BasicList<PLib::HPoint_nD<double, 3> >::add)
        .def("addElements", &BasicList<PLib::HPoint_nD<double, 3> >::addElements)
        //.def("remove", &BasicList<PLib::HPoint_nD<double, 3> >::remove)
        .def("erase", &BasicList<PLib::HPoint_nD<double, 3> >::erase)
        //.def("goToFirst", &BasicList<PLib::HPoint_nD<double, 3> >::goToFirst)
        //.def("goToNext", &BasicList<PLib::HPoint_nD<double, 3> >::goToNext)
        //.def("goToPrevious", &BasicList<PLib::HPoint_nD<double, 3> >::goToPrevious)
        .def("size", &BasicList<PLib::HPoint_nD<double, 3> >::size)
        .def("resetMode", &BasicList<PLib::HPoint_nD<double, 3> >::resetMode)
        .def("setResetMode", &BasicList<PLib::HPoint_nD<double, 3> >::setResetMode)
    );

    enum_< BasicList<PLib::HPoint_nD<double, 3> >::ListResetMode >("ListResetMode")
        .value("delete_at_reset", BasicList<PLib::HPoint_nD<double, 3> >::delete_at_reset)
        .value("keep_at_reset", BasicList<PLib::HPoint_nD<double, 3> >::keep_at_reset)
    ;

    delete BasicList_HPoint3Dd_scope;

    scope* BasicList_HPoint2Dd_scope = new scope(
    class_< BasicList<PLib::HPoint_nD<double, 2> >, boost::noncopyable >("BasicList_HPoint2Dd", init<  >())
        .def(init< BasicList<PLib::HPoint_nD<double, 2> >& >())
        .def_readwrite("current", &BasicList<PLib::HPoint_nD<double, 2> >::current)
        .def_readwrite("data", &BasicNode<PLib::HPoint_nD<double, 2> >::data)
        .def_readwrite("prev", &BasicNode<PLib::HPoint_nD<double, 2> >::prev)
        .def_readwrite("next", &BasicNode<PLib::HPoint_nD<double, 2> >::next)
        //.def("first", &BasicList<PLib::HPoint_nD<double, 2> >::first)
        //.def("last", &BasicList<PLib::HPoint_nD<double, 2> >::last)
        .def("reset", &BasicList<PLib::HPoint_nD<double, 2> >::reset)
        .def("add", (void (BasicList<PLib::HPoint_nD<double, 2> >::*)(BasicNode<PLib::HPoint_nD<double, 2> >*) )&BasicList<PLib::HPoint_nD<double, 2> >::add)
        .def("add", (void (BasicList<PLib::HPoint_nD<double, 2> >::*)(const PLib::HPoint_nD<double,2>&) )&BasicList<PLib::HPoint_nD<double, 2> >::add)
        .def("addElements", &BasicList<PLib::HPoint_nD<double, 2> >::addElements)
        //.def("remove", &BasicList<PLib::HPoint_nD<double, 2> >::remove)
        .def("erase", &BasicList<PLib::HPoint_nD<double, 2> >::erase)
        //.def("goToFirst", &BasicList<PLib::HPoint_nD<double, 2> >::goToFirst)
        //.def("goToNext", &BasicList<PLib::HPoint_nD<double, 2> >::goToNext)
        //.def("goToPrevious", &BasicList<PLib::HPoint_nD<double, 2> >::goToPrevious)
        .def("size", &BasicList<PLib::HPoint_nD<double, 2> >::size)
        .def("resetMode", &BasicList<PLib::HPoint_nD<double, 2> >::resetMode)
        .def("setResetMode", &BasicList<PLib::HPoint_nD<double, 2> >::setResetMode)
    );

    enum_< BasicList<PLib::HPoint_nD<double, 2> >::ListResetMode >("ListResetMode")
        .value("delete_at_reset", BasicList<PLib::HPoint_nD<double, 2> >::delete_at_reset)
        .value("keep_at_reset", BasicList<PLib::HPoint_nD<double, 2> >::keep_at_reset)
    ;

    delete BasicList_HPoint2Dd_scope;

    class_< PLib::BasicArray<PLib::Point_nD<double, 3> >, BasicArray_Point3Dd_Wrapper >("BasicArray_Point3Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::BasicArray<PLib::Point_nD<double, 3> >& >())
        .def(init< PLib::Point3Dd*, const int >())
        .def(init< BasicList<PLib::Point_nD<double, 3> >& >())
        .def("reset", &PLib::BasicArray<PLib::Point_nD<double, 3> >::reset, &BasicArray_Point3Dd_Wrapper::default_reset_1)
        .def("reset", &BasicArray_Point3Dd_Wrapper::default_reset_0)
        .def("n", &PLib::BasicArray<PLib::Point_nD<double, 3> >::n)
        .def("size", &PLib::BasicArray<PLib::Point_nD<double, 3> >::size)
        .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)(const int) )&PLib::BasicArray<PLib::Point_nD<double, 3> >::resize)
        .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)(const PLib::BasicArray<PLib::Point_nD<double, 3> >&) )&PLib::BasicArray<PLib::Point_nD<double, 3> >::resize)
        .def("trim", &PLib::BasicArray<PLib::Point_nD<double, 3> >::trim)
        .def("clear", &PLib::BasicArray<PLib::Point_nD<double, 3> >::clear)
        .def("untrim", &PLib::BasicArray<PLib::Point_nD<double, 3> >::untrim)
        //.def("push_back", &PLib::BasicArray<PLib::Point_nD<double, 3> >::push_back, BasicArray_Point3Dd_push_back_overloads_1_3())
        //.def("memory", &PLib::BasicArray<PLib::Point_nD<double, 3> >::memory)
        .def("width", &PLib::BasicArray<PLib::Point_nD<double, 3> >::width)
        //.def("print", &PLib::BasicArray<PLib::Point_nD<double, 3> >::print)
        //.def("begin", (PLib::Point3Dd* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 3> >::begin)
        //.def("begin", (const PLib::Point3Dd* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 3> >::begin)
        //.def("end", (PLib::Point3Dd* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 3> >::end)
        //.def("end", (const PLib::Point3Dd* (PLib::BasicArray<PLib::Point_nD<double, 3> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 3> >::end)
        .def( self == self )
        .def( self != self )
        .def(self_ns::str(self))
        //.def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
    ;

    class_< PLib::BasicArray<PLib::Point_nD<double, 2> >, BasicArray_Point2Dd_Wrapper >("BasicArray_Point2Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::BasicArray<PLib::Point_nD<double, 2> >& >())
        .def(init< PLib::Point2Dd*, const int >())
        .def(init< BasicList<PLib::Point_nD<double, 2> >& >())
        .def("reset", &PLib::BasicArray<PLib::Point_nD<double, 2> >::reset, &BasicArray_Point2Dd_Wrapper::default_reset_1)
        .def("reset", &BasicArray_Point2Dd_Wrapper::default_reset_0)
        .def("n", &PLib::BasicArray<PLib::Point_nD<double, 2> >::n)
        .def("size", &PLib::BasicArray<PLib::Point_nD<double, 2> >::size)
        .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)(const int) )&PLib::BasicArray<PLib::Point_nD<double, 2> >::resize)
        .def("resize", (void (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)(const PLib::BasicArray<PLib::Point_nD<double, 2> >&) )&PLib::BasicArray<PLib::Point_nD<double, 2> >::resize)
        .def("trim", &PLib::BasicArray<PLib::Point_nD<double, 2> >::trim)
        .def("clear", &PLib::BasicArray<PLib::Point_nD<double, 2> >::clear)
        .def("untrim", &PLib::BasicArray<PLib::Point_nD<double, 2> >::untrim)
        //.def("push_back", &PLib::BasicArray<PLib::Point_nD<double, 2> >::push_back, BasicArray_Point2Dd_push_back_overloads_1_3())
        //.def("memory", &PLib::BasicArray<PLib::Point_nD<double, 2> >::memory)
        .def("width", &PLib::BasicArray<PLib::Point_nD<double, 2> >::width)
        //.def("print", &PLib::BasicArray<PLib::Point_nD<double, 2> >::print)
        //.def("begin", (PLib::Point2Dd* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 2> >::begin)
        //.def("begin", (const PLib::Point2Dd* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 2> >::begin)
        //.def("end", (PLib::Point2Dd* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() )&PLib::BasicArray<PLib::Point_nD<double, 2> >::end)
        //.def("end", (const PLib::Point2Dd* (PLib::BasicArray<PLib::Point_nD<double, 2> >::*)() const)&PLib::BasicArray<PLib::Point_nD<double, 2> >::end)
        .def(self_ns::str(self))
        .def( self != self )
        //.def( other< std::basic_istream<char,std::char_traits<char> > >() >> self )
        .def( self == self )
    ;


    class_< PLib::BasicArray<PLib::HPoint_nD<double, 3> >, BasicArray_HPoint3Dd_Wrapper >("BasicArray_HPoint3Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::BasicArray<PLib::HPoint_nD<double, 3> >& >())
        .def(init< PLib::HPoint_nD<double,3>*, const int >())
        .def(init< BasicList<PLib::HPoint_nD<double, 3> >& >())
        .def("reset", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::reset, &BasicArray_HPoint3Dd_Wrapper::default_reset_1)
        .def("reset", &BasicArray_HPoint3Dd_Wrapper::default_reset_0)
        .def("n", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::n)
        .def("size", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::size)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)(const int) )&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::resize)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 3> >::*)(const PLib::BasicArray<PLib::HPoint_nD<double, 3> >&) )&PLib::BasicArray<PLib::HPoint_nD<double, 3> >::resize)
        .def("trim", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::trim)
        .def("clear", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::clear)
        .def("untrim", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::untrim)
//         .def("push_back", &PLib::BasicArray<PLib::HPoint_nD<double, 3> >::push_back, BasicArray_HPoint3Dd_push_back_overloads_1_3())
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

    class_< PLib::BasicArray<PLib::HPoint_nD<double, 2> >, BasicArray_HPoint2Dd_Wrapper >("BasicArray_HPoint2Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::BasicArray<PLib::HPoint_nD<double, 2> >& >())
        .def(init< PLib::HPoint_nD<double,2>*, const int >())
        .def(init< BasicList<PLib::HPoint_nD<double, 2> >& >())
        .def("reset", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::reset, &BasicArray_HPoint2Dd_Wrapper::default_reset_1)
        .def("reset", &BasicArray_HPoint2Dd_Wrapper::default_reset_0)
        .def("n", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::n)
        .def("size", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::size)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)(const int) )&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("resize", (void (PLib::BasicArray<PLib::HPoint_nD<double, 2> >::*)(const PLib::BasicArray<PLib::HPoint_nD<double, 2> >&) )&PLib::BasicArray<PLib::HPoint_nD<double, 2> >::resize)
        .def("trim", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::trim)
        .def("clear", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::clear)
        .def("untrim", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::untrim)
//         .def("push_back", &PLib::BasicArray<PLib::HPoint_nD<double, 2> >::push_back, BasicArray_HPoint2Dd_push_back_overloads_1_3())
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
    ;

    class_< PLib::Vector<PLib::Point_nD<double, 3> >, bases< PLib::BasicArray<PLib::Point_nD<double, 3> > >  >("Vector_Point3Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::Vector<PLib::Point_nD<double, 3> >& >())
        .def(init< const PLib::BasicArray<PLib::Point_nD<double, 3> >& >())
        .def(init< PLib::Point3Dd*, const int >())
        .def(init< BasicList<PLib::Point_nD<double, 3> >& >())
        .def("rows", &PLib::Vector<PLib::Point_nD<double, 3> >::rows)
        .def("as", &PLib::Vector<PLib::Point_nD<double, 3> >::as)
        .def("get", &PLib::Vector<PLib::Point_nD<double, 3> >::get)
        .def("minIndex", &PLib::Vector<PLib::Point_nD<double, 3> >::minIndex)
        .def("minimum", &PLib::Vector<PLib::Point_nD<double, 3> >::minimum)
        .def("qSortStd", &PLib::Vector<PLib::Point_nD<double, 3> >::qSortStd)
        .def("qSort", &PLib::Vector<PLib::Point_nD<double, 3> >::qSort, Vector_Point3Dd_qSort_overloads_0_1())
        .def("sortIndex", &PLib::Vector<PLib::Point_nD<double, 3> >::sortIndex, Vector_Point3Dd_sortIndex_overloads_1_2())
        .def( self * self )
        .def( other< double >() * self )
        .def( self * other< std::complex<double> >() )
        .def( self * other< double >() )
        .def( self - self )
        .def( self + self )
        .def( other< std::complex<double> >() * self )
        .def( self == self )
        .def( self != self )
        .def( self += self )
        .def( self -= self )
    ;

    class_< PLib::Vector<PLib::Point_nD<double, 2> >, bases< PLib::BasicArray<PLib::Point_nD<double, 2> > >  >("Vector_Point2Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::Vector<PLib::Point_nD<double, 2> >& >())
        .def(init< const PLib::BasicArray<PLib::Point_nD<double, 2> >& >())
        .def(init< PLib::Point2Dd*, const int >())
        .def(init< BasicList<PLib::Point_nD<double, 2> >& >())
        .def("rows", &PLib::Vector<PLib::Point_nD<double, 2> >::rows)
        .def("as", &PLib::Vector<PLib::Point_nD<double, 2> >::as)
        .def("get", &PLib::Vector<PLib::Point_nD<double, 2> >::get)
        .def("minIndex", &PLib::Vector<PLib::Point_nD<double, 2> >::minIndex)
        .def("minimum", &PLib::Vector<PLib::Point_nD<double, 2> >::minimum)
        .def("qSortStd", &PLib::Vector<PLib::Point_nD<double, 2> >::qSortStd)
        .def("qSort", &PLib::Vector<PLib::Point_nD<double, 2> >::qSort, Vector_Point2Dd_qSort_overloads_0_1())
        .def("sortIndex", &PLib::Vector<PLib::Point_nD<double, 2> >::sortIndex, Vector_Point2Dd_sortIndex_overloads_1_2())
        .def( self - self )
        .def( self * other< std::complex<double> >() )
        .def( self * other< double >() )
        .def( self * self )
        .def( self + self )
        .def( other< double >() * self )
        .def( other< std::complex<double> >() * self )
        .def( self == self )
        .def( self != self )
        .def( self += self )
        .def( self -= self )
    ;

    class_< PLib::Vector<PLib::HPoint_nD<double, 3> >, bases< PLib::BasicArray<PLib::HPoint_nD<double, 3> > >  >("Vector_HPoint3Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::Vector<PLib::HPoint_nD<double, 3> >& >())
        .def(init< const PLib::BasicArray<PLib::HPoint_nD<double, 3> >& >())
        .def(init< PLib::HPoint3Dd*, const int >())
        .def(init< BasicList<PLib::HPoint_nD<double, 3> >& >())
        .def("rows", &PLib::Vector<PLib::HPoint_nD<double, 3> >::rows)
        .def("as", &PLib::Vector<PLib::HPoint_nD<double, 3> >::as)
        .def("get", &PLib::Vector<PLib::HPoint_nD<double, 3> >::get)
        .def("minIndex", &PLib::Vector<PLib::HPoint_nD<double, 3> >::minIndex)
        .def("minimum", &PLib::Vector<PLib::HPoint_nD<double, 3> >::minimum)
        .def("qSortStd", &PLib::Vector<PLib::HPoint_nD<double, 3> >::qSortStd)
        .def("qSort", &PLib::Vector<PLib::HPoint_nD<double, 3> >::qSort, Vector_HPoint3Dd_qSort_overloads_0_1())
        .def("sortIndex", &PLib::Vector<PLib::HPoint_nD<double, 3> >::sortIndex, Vector_HPoint3Dd_sortIndex_overloads_1_2())
        .def( self * self )
        .def( other< double >() * self )
        .def( self * other< std::complex<double> >() )
        .def( self * other< double >() )
        .def( self - self )
        .def( self + self )
        .def( other< std::complex<double> >() * self )
        .def( self == self )
        .def( self != self )
        .def( self += self )
        .def( self -= self )
    ;

    class_< PLib::Vector<PLib::HPoint_nD<double, 2> >, bases< PLib::BasicArray<PLib::HPoint_nD<double, 2> > >  >("Vector_HPoint2Dd", init<  >())
        .def(init< const int >())
        .def(init< const PLib::Vector<PLib::HPoint_nD<double, 2> >& >())
        .def(init< const PLib::BasicArray<PLib::HPoint_nD<double, 2> >& >())
        .def(init< PLib::HPoint2Dd*, const int >())
        .def(init< BasicList<PLib::HPoint_nD<double, 2> >& >())
        .def("rows", &PLib::Vector<PLib::HPoint_nD<double, 2> >::rows)
        .def("as", &PLib::Vector<PLib::HPoint_nD<double, 2> >::as)
        .def("get", &PLib::Vector<PLib::HPoint_nD<double, 2> >::get)
        .def("minIndex", &PLib::Vector<PLib::HPoint_nD<double, 2> >::minIndex)
        .def("minimum", &PLib::Vector<PLib::HPoint_nD<double, 2> >::minimum)
        .def("qSortStd", &PLib::Vector<PLib::HPoint_nD<double, 2> >::qSortStd)
        .def("qSort", &PLib::Vector<PLib::HPoint_nD<double, 2> >::qSort, Vector_HPoint2Dd_qSort_overloads_0_1())
        .def("sortIndex", &PLib::Vector<PLib::HPoint_nD<double, 2> >::sortIndex, Vector_HPoint2Dd_sortIndex_overloads_1_2())
        .def( self - self )
        .def( self * other< std::complex<double> >() )
        .def( self * other< double >() )
        .def( self * self )
        .def( self + self )
        .def( other< double >() * self )
        .def( other< std::complex<double> >() * self )
        .def( self == self )
        .def( self != self )
        .def( self += self )
        .def( self -= self )
    ;

}

