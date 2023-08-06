//  Copyright Joel de Guzman 2002-2004. Distributed under the Boost
//  Software License, Version 1.0. (See accompanying file LICENSE_1_0.txt
//  or copy at http://www.boost.org/LICENSE_1_0.txt)
//  Hello World Example from the tutorial
//  [Joel de Guzman 10/9/2002]

#include <boost/python.hpp>
#include <bm.h>
#include <bmserial.h>

using namespace std;
typedef bm::bvector<> bvect_t;

void optimize(bvect_t *v) {
	v->optimize();
}

void set_noarg(bvect_t *v) {
	v->set();
}

PyObject *serialize(bvect_t& v) {
	PyObject *s;
	int len;
	bvect_t::statistics st;
	bm::serializer<bm::bvector<> > bvs;

	v.optimize();
	v.calc_stat(&st);

	// lowest serialised size
	bvs.byte_order_serialization(false);
	bvs.gap_length_serialization(false);
	bvs.set_compression_level(4);

	s = PyString_FromStringAndSize(NULL, st.max_serialize_mem);
	len = bvs.serialize(v, (unsigned char *)PyString_AsString(s), st.max_serialize_mem);
	_PyString_Resize(&s, len);

	return s;
}

void deserialize(bvect_t& v, PyObject *o) {
	Py_buffer view;

	if(!PyObject_CheckBuffer(o)) {
		printf("Not a buffer!\n");
		return;
	}
	PyObject_GetBuffer(o, &view, PyBUF_SIMPLE);
	
	bm::deserialize(v, (unsigned char *)view.buf);

	PyBuffer_Release(&view);
}

BOOST_PYTHON_MODULE(bm_ext)
{
	using namespace boost::python;

	enum_<bm::strategy>("strat")
		.value("BIT", bm::BM_BIT)
		.value("GAP", bm::BM_GAP)
	;

	class_<bvect_t>("bvector")
		.def("count", &bvect_t::count)
		.def("__len__", &bvect_t::size)
		.def("resize", &bvect_t::resize)
		.def("capacity", &bvect_t::capacity)

		.def("__getitem__", &bvect_t::get_bit)
		.def("__setitem__", &bvect_t::set_bit)
		.def("set", set_noarg)
		.def("clear", &bvect_t::clear)
		.def("any", &bvect_t::any)
		.def("none", &bvect_t::none)

		.def(~self)
		.def(self == other<bvect_t>())
		.def(self != other<bvect_t>())
		.def(self < other<bvect_t>())
		.def(self > other<bvect_t>())
		.def(self <= other<bvect_t>())
		.def(self >= other<bvect_t>())
		.def(self - other<bvect_t>())
		.def(self & other<bvect_t>())
		.def(self | other<bvect_t>())
		.def(self ^ other<bvect_t>())

		.def("calc_stat", &bvect_t::calc_stat)
		.def("optimize", optimize)
		.def("serialize", serialize)
		.def("deserialize", deserialize)
		.def("set_new_blocks_strat", &bvect_t::set_new_blocks_strat)
	;
	class_<bvect_t::enumerator>("enumerator", init<bvect_t *, int>())
		.def(self < other<bvect_t::enumerator>())
		.def(self > other<bvect_t::enumerator>())
		.def(self <= other<bvect_t::enumerator>())
		.def(self >= other<bvect_t::enumerator>())
		.def("value", &bvect_t::enumerator::value)
		.def("next", &bvect_t::enumerator::go_up, return_value_policy<reference_existing_object>())
	;
	class_<bvect_t::statistics>("statistics")
		.def_readonly("bit_blocks", &bvect_t::statistics::bit_blocks)
		.def_readonly("gap_blocks", &bvect_t::statistics::gap_blocks)
		.def_readonly("memory_used", &bvect_t::statistics::memory_used)
		.def_readonly("max_serialize_mem", &bvect_t::statistics::max_serialize_mem)
	;
}

