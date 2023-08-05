
import java.io.*;
import java.util.*;

import org.clearsilver.CS;
import org.clearsilver.HDF;

class CSTest {

    public static void main( String [] args ) throws IOException {
        org.clearsilver.HDF hdf = new HDF();

        System.out.println("Testing HDF set and dump\n");
        hdf.setValue("Foo.Bar","10");
        hdf.setValue("Foo.Baz","20");
        System.out.println( hdf.dump() );

        System.out.println("Testing HDF get\n");
        String foo = hdf.getValue("Foo.Bar", "30");
        System.out.println( foo );
        foo = hdf.getValue("Foo.Baz", "30");
        System.out.println( foo );

        System.out.println( "----" );

        System.out.println("Testing HDF get where default value is null\n");
        foo = hdf.getValue("Foo.Bar", null);
        System.out.println("foo = " + foo);
        foo = hdf.getValue("Foo.Nonexistent", null);
        System.out.println("foo = " + foo);

        System.out.println( "----" );

        int fooInt = hdf.getIntValue("Foo.Bar", 30);
        System.out.println("Testing HDF get int\n");
        System.out.println( fooInt );

        System.out.println( "----" );

        org.clearsilver.CS cs = new CS(hdf);
        
        System.out.println("Testing HDF parse/render\n");
        String tmplstr = "Foo.Bar:<?cs var:Foo.Bar ?>\nFoo.Baz:<?cs var:Foo.Baz ?>\n";
        System.out.println(tmplstr);
        System.out.println("----");

        cs.parseStr(tmplstr);
        System.out.println(cs.render());

        // test registered functions
        System.out.println("Testing registered string functions\n");
        hdf.setValue("Foo.EscapeTest","abc& 231<>/?");
   
        tmplstr = " <?cs var:url_escape(Foo.EscapeTest) ?> <?cs var:html_escape(Foo.EscapeTest) ?>";

        cs.parseStr(tmplstr);
        System.out.println(cs.render());

        cs = new CS(hdf);

        System.out.println("Testing white space stripping\n");
        // test white space stripping
        tmplstr = "      <?cs var:Foo.Bar ?> This is a       string     without whitespace stripped";
        cs.parseStr(tmplstr);
        System.out.println(cs.render());

        hdf.setValue("ClearSilver.WhiteSpaceStrip", "1");
        System.out.println(cs.render());

        // Now, test debug dump
        System.out.println("Testing debug dump\n");
        hdf.setValue("ClearSilver.DisplayDebug", "1");
        System.out.println(cs.render());
        
        System.out.println("Final HDF dump\n");
        System.out.println( hdf.dump() );

            // Now, test reading an HDF file from disk
        System.out.println("Testing HDF.readFile()\n");
        HDF file_hdf = new HDF();
        file_hdf.readFile("testdata/test1.hdf");
        System.out.println(file_hdf.dump());

        System.out.println("Testing HDF.readFile() for a file that doesn't exist");
        try {
          file_hdf.readFile("testdata/doesnt_exist.hdf");
        } catch (Exception e) {
          // The error message contains line numbers for functions in
          // neo_hdf.c, and I don't want this test to fail if the line numbers
          // change, so I'm not going to print out the exception message here.
          // The important thing to test here is that an exception is thrown 
          // System.out.println(e + "\n");
          System.out.println("Caught exception of type " + e.getClass().getName() + "\n");
        }

        System.out.println("Testing HDF.getObj()");
        HDF foo_hdf = file_hdf.getObj("Foo");
        System.out.println(foo_hdf.dump());

        System.out.println("Testing HDF.objName()");
        System.out.println("Should be \"Foo\": " + foo_hdf.objName());
        System.out.println("Should be \"Bar\": "
                           + foo_hdf.getObj("Bar").objName());
        System.out.println("Should be null: " + file_hdf.objName() + "\n");

        System.out.println("Testing HDF.objValue()");
        System.out.println("Value of Foo.Bar: "
                           + foo_hdf.getObj("Bar").objValue());
        System.out.println("Value of root node: " + file_hdf.objValue() + "\n");

        System.out.println("Testing HDF.objChild()");
        HDF child_hdf = foo_hdf.objChild();
        System.out.println("First child name: " + child_hdf.objName() + "\n");

        System.out.println("Testing HDF.objNext()");
        HDF next_hdf = child_hdf.objNext();
        System.out.println("Next child name: " + next_hdf.objName());
        next_hdf = next_hdf.objNext();
        System.out.println("Next child (should be null): " + next_hdf + "\n");
    }
};
