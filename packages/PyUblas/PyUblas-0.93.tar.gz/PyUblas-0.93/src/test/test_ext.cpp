#include <iostream>
#include <algorithm>
#include <vector>
#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/vector.hpp>
#include <boost/numeric/ublas/io.hpp>
#include <pyublas/numpy.hpp>
#include <boost/foreach.hpp>
#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>




using namespace boost::python;
using namespace pyublas;
namespace ublas = boost::numeric::ublas;




template <class T>
T doublify(T x)
{
  return 2*x;
}




template <class T>
void doublify_inplace(T x)
{
  x *= 2;
}




template <class T>
numpy_vector<T> doublify_strided(numpy_strided_vector<T> x)
{
  return 2*x;
}




/* The following two versions preserve shape on output: */
template <class T>
numpy_vector<T> doublify_keep_shape_1(numpy_vector<T> x)
{
  numpy_vector<T> result(x.ndim(), x.dims());
  result.assign(2*x.as_strided());
  return result;
}




template <class T>
numpy_vector<T> doublify_keep_shape_2(numpy_vector<T> x)
{
  numpy_vector<T> result(2*x.as_strided());
  result.reshape(x.ndim(), x.dims());
  return result;
}




template <class T>
void doublify_numpy_vector_inplace(numpy_vector<T> x)
{
  x *= 2;
}




template <class T>
void doublify_numpy_strided_vector_inplace(numpy_strided_vector<T> x)
{
  x *= 2;
}




numpy_vector<double> make_resized_vector(unsigned n)
{
  numpy_vector<double> result;
  result.resize(n);
  return result;
}




BOOST_PYTHON_MODULE(test_ext)
{
  def("dbl_int", doublify<int>);
  def("dbl_float", doublify<double>);

  def("dbl_numpy_mat", doublify<numpy_matrix<double> >);
  def("dbl_numpy_mat_cm", 
      doublify<numpy_matrix<double, ublas::column_major> >);

  def("dbl_numpy_mat_inplace", doublify_inplace<numpy_matrix<double> >);
  def("dbl_numpy_mat_cm_inplace", 
      doublify_inplace<numpy_matrix<double, ublas::column_major> >);

  def("dbl_numpy_vec", 
      doublify<numpy_vector<double> >);
  def("dbl_numpy_vec_keep_shape_1", 
      doublify_keep_shape_1<double>);
  def("dbl_numpy_vec_keep_shape_2", 
      doublify_keep_shape_2<double>);
  def("dbl_numpy_strided_vec", 
      doublify_strided<double>);
  def("dbl_numpy_vec_inplace", 
      doublify_numpy_vector_inplace<double>);
  def("dbl_numpy_strided_vec_inplace", 
      doublify_numpy_strided_vector_inplace<double>);
  def("dbl_numpy_strided_vec_inplace", 
      doublify_numpy_strided_vector_inplace<double>);
  def("dbl_ublas_vec", 
      doublify<ublas::vector<double> >);
  def("dbl_ublas_mat", 
      doublify<ublas::matrix<double> >);

  def("make_resized_vector", make_resized_vector);
}
