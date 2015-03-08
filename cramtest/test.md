# Testing ODP generator

## Some paragraphs with code

Example setup per host:

    Host funny-3
       Hostname funny-3.example.com
       User test

Note: this is ***important*** *as* "blafasl" uses <short> hostnames.

## Some outline text

* Install this and that, and add the wombat ISO on top
* Add test user to each item - `$ blafasl` for example
  * sub item - this is ™ me

~~~ bash
      # rm -rf /
~~~

## Slide as before in markdown

    ## Some outline text

    * Install this and that, and add the wombat ISO on top
    * Add test user to each item - `$ blafasl` for example
      * sub item - this is ™ me

    ~~~ bash
          # rm -rf /
    ~~~

## Some actual code

~~~ c++
::basegfx::B2DPolyPolygon VeeWipe::operator () ( double t )
{
    ::basegfx::B2DPolygon poly;
    poly.append( ::basegfx::B2DPoint( 0.0, -1.0 ) );
    const double d = ::basegfx::pruneScaleValue( 2.0 * t );
    poly.append( ::basegfx::B2DPoint(
           0.0, d - 1.0 ) );
    poly.append( ::basegfx::B2DPoint(
           0.5, d ) );
    poly.append( ::basegfx::B2DPoint(
           1.0, d - 1.0 ) );
    poly.append( ::basegfx::B2DPoint(
           1.0, -1.0 ) );
    poly.setClosed(true);
    return ::basegfx::B2DPolyPolygon( poly );
}
~~~

## Test image

![This is alt text](http://upload.wikimedia.org/wikipedia/commons/0/02/LibreOffice_Logo_Flat.svg "This is optional title for a direct img")

## Test image 2

![This is alt text](http://upload.wikimedia.org/wikipedia/commons/0/02/LibreOffice_Logo_Flat.svg)

## Test image ref

![This is alt text][1]

## Test URLs

This is [an example](http://example.com/ "Title") inline link.
This is [an example][2] reference-style link.

[1]: https://wiki.documentfoundation.org/images/8/87/LibreOffice_external_logo_600px.png  "This is optional title attribute for a ref img"
[2]: http://example.com/  "Optional Title Here"

