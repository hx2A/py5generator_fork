/* ****************************************************************************

  Part of the py5 library
  Copyright (C) 2020-2025 Jim Schmitz

  This library is free software: you can redistribute it and/or modify it
  under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation, either version 2.1 of the License, or (at
  your option) any later version.

  This library is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
  General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this library. If not, see <https://www.gnu.org/licenses/>.

******************************************************************************/
package py5.core;

public interface Py5Bridge {

  public String[] get_function_list();

  public void terminate_sketch();

  public boolean run_method(String method_name, Object... params);

  public Object call_function(String key, Object... params);

  public void py5_println(String text, boolean stderr);

  public void focus_window(long handle);

  public void shutdown();

}
