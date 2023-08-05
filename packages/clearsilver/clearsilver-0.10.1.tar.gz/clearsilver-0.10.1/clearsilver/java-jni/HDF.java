package org.clearsilver;

import java.io.FileNotFoundException;
import java.io.IOException;

/** This class is a wrapper around the HDF C API.  Many features of the C API
 *  are not yet exposed through this wrapper.
 */
public class HDF {
  int hdfptr;  // stores the C HDF* pointer
  HDF root;    // If this is a child HDF node, points at the root node of
               // the tree.  For root nodes this is null.  A child node needs
               // to hold a reference on the root to prevent the root from
               // being GC-ed.
  static { 
    try {
      System.loadLibrary("clearsilver-jni");
    } catch ( UnsatisfiedLinkError e ) {
      System.out.println("Could not load 'clearsilver-jni'");
      System.exit(1);
    }
  }
   
  /** Constructs an empty HDF dataset */
  public HDF() {
    hdfptr = _init();
    root = null;
  }

  /** Constructs an HDF child node.  Used by other methods in this class when
   * a child node needs to be constructed.
   */
  private HDF(int hdfptr, HDF parent) {
    this.hdfptr = hdfptr;
    this.root = (parent.root != null) ? parent.root : parent;
  }

  public void finalize() {
    // Only root nodes have ownership of the C HDF pointer, so only a root
    // node needs to dealloc hdfptr.
    if ( root == null ) {
      _dealloc(hdfptr);
    }
  }

  /** Loads the contents of the specified HDF file from disk into the current
   *  HDF object.  The loaded contents are merged with the existing contents.
   */
  public boolean readFile(String filename) throws IOException,
         FileNotFoundException {
    return _readFile(hdfptr, filename);
  }

  /** Retrieves the integer value at the specified path in this HDF node's
   *  subtree.  If the value does not exist, or cannot be converted to an
   *  integer, default_value will be returned. */
  public int getIntValue(String hdfname, int default_value) {
    return _getIntValue(hdfptr,hdfname,default_value);
  }

  /** Retrieves the value at the specified path in this HDF node's subtree.
  */
  public String getValue(String hdfname, String default_value) {
    return _getValue(hdfptr,hdfname,default_value);
  }

  /** Sets the value at the specified path in this HDF node's subtree. */
  public void setValue(String hdfname, String value) {
    _setValue(hdfptr,hdfname,value);
  }

  /** Retrieves the HDF object that is the root of the subtree at hdfpath, or
   *  null if no object exists at that path. */
  public HDF getObj(String hdfpath) {
    int obj_ptr = _getObj(hdfptr, hdfpath);
    if ( obj_ptr == 0 ) {
      return null;
    }
    return new HDF(obj_ptr, this);
  }

  /** Returns the name of this HDF node.   The root node has no name, so
   *  calling this on the root node will return null. */
  public String objName() {
    return _objName(hdfptr);
  }

  /** Returns the value of this HDF node, or null if this node has no value.
   *  Every node in the tree can have a value, a child, and a next peer. */
  public String objValue() {
    return _objValue(hdfptr);
  }

  /** Returns the child of this HDF node, or null if there is no child.
   *  Use this in conjunction with objNext to walk the HDF tree.  Every node
   *  in the tree can have a value, a child, and a next peer. */
  public HDF objChild() {
    int child_ptr = _objChild(hdfptr);
    if ( child_ptr == 0 ) {
      return null;
    }
    return new HDF(child_ptr, this);
  }

  /** Returns the next sibling of this HDF node, or null if there is no next
   *  sibling.  Use this in conjunction with objChild to walk the HDF tree.
   *  Every node in the tree can have a value, a child, and a next peer. */
  public HDF objNext() {
    int next_ptr = _objNext(hdfptr);
    if ( next_ptr == 0 ) {
      return null;
    }
    return new HDF(next_ptr, this);
  }

  /**
   * Generates a string representing the content of the HDF tree rooted at
   * this node.
   */
  public String dump() {
    return _dump(hdfptr);
  }

  private static native int _init();
  private static native void _dealloc(int ptr);
  private static native boolean _readFile(int ptr, String filename);
  private static native int _getIntValue(int ptr, String hdfname,
                                         int default_value);
  private static native String _getValue(int ptr, String hdfname,
                                         String default_value);
  private static native void _setValue(int ptr, String hdfname,
                                       String hdf_value);
  private static native int _getObj(int ptr, String hdfpath);
  private static native int _objChild(int ptr);
  private static native int _objNext(int ptr);
  private static native String _objName(int ptr);
  private static native String _objValue(int ptr);

  private static native String _dump(int ptr);
}

