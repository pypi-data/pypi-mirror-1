/*******************************************************************************
 * 
 * Copyright (c) 2009, 2010, Barthelemy Dagenais All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * 
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *******************************************************************************/
package py4j;

/**
 * <p>
 * This class defines the protocol used to communicate between two virtual
 * machines (e.g., Python and Java).
 * </p>
 * <p>
 * Currently, the protocol requires type information (e.g., is this string an
 * integer, an object reference or a boolean?) to be embedded with each command
 * part. The rational is that the source virtual machine is usually better at
 * determining the type of objects it sends.
 * </p>
 * <p>
 * An input command is usually composed of:
 * </p>
 * <ul>
 * <li>A command name (e.g., c for call)</li>
 * <li>Optionally, a sub command name (e.g., a for concatenate in the list
 * command)</li>
 * <li>A list of command parts (e.g., the name of a method, the value of a
 * parameter, etc.)</li>
 * <li>The End of Command marker (e)</li>
 * </ul>
 * 
 * <p>
 * The various parts of a command are separated by \n characters. These
 * characters are automatically escaped and unescaped in Strings on both sides
 * (Java and Python).
 * </p>
 * 
 * <p>
 * An output command is usually composed of:
 * </p>
 * <ul>
 * <li>A success or error code (y for yes, x for exception)</li>
 * <li>A return value (e.g., n for null, v for void, or any other value like a
 * String)</li>
 * </ul>
 * 
 * <p>This class should be used only if the user creates new commands.</p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class Protocol {

	// TYPES
	public final static char INTEGER_TYPE = 'i';
	public final static char BOOLEAN_TYPE = 'b';
	public final static char DOUBLE_TYPE = 'd';
	public final static char STRING_TYPE = 's';
	public final static char REFERENCE_TYPE = 'r';
	public final static char LIST_TYPE = 'l';
	public final static char MAP_TYPE = 'a';
	public final static char NULL_TYPE = 'n';

	public final static char PACKAGE_TYPE = 'p';
	public final static char CLASS_TYPE = 'c';
	public final static char METHOD_TYPE = 'm';
	public final static char NO_MEMBER = 'o';
	public final static char VOID = 'v';

	// END OF COMMAND MARKER
	public final static char END = 'e';
	public final static char END_OUTPUT = '\n';

	// OUTPUT VALUES
	public final static char ERROR = 'x';
	public final static char SUCCESS = 'y';

	// SHORTCUT
	public final static String ERROR_COMMAND = "" + ERROR + END_OUTPUT;
	public final static String VOID_COMMAND = "" + SUCCESS + VOID + END_OUTPUT;
	public final static String NO_SUCH_FIELD = "" + SUCCESS + NO_MEMBER
			+ END_OUTPUT;

	// ENTRY POINT
	public final static String ENTRY_POINT_OBJECT_ID = "t";

	// STATIC REFERENCES
	public final static String STATIC_PREFIX = "z:";

	public final static boolean isEmpty(String commandPart) {
		return commandPart == null || commandPart.trim().length() == 0;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is the end token
	 */
	public final static boolean isEnd(String commandPart) {
		return commandPart.length() == 1 && commandPart.charAt(0) == 'e';
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is an integer
	 */
	public final static boolean isInteger(String commandPart) {
		return commandPart.charAt(0) == INTEGER_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The integer value corresponding to this command part.
	 */
	public final static int getInteger(String commandPart) {
		return Integer.parseInt(commandPart.substring(1, commandPart.length()));
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a boolean
	 */
	public final static boolean isBoolean(String commandPart) {
		return commandPart.charAt(0) == BOOLEAN_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The boolean value corresponding to this command part.
	 */
	public final static boolean getBoolean(String commandPart) {
		return Boolean.parseBoolean(commandPart.substring(1, commandPart
				.length()));
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a double
	 */
	public final static boolean isDouble(String commandPart) {
		return commandPart.charAt(0) == DOUBLE_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The double value corresponding to this command part.
	 */
	public final static double getDouble(String commandPart) {
		return Double.parseDouble(commandPart
				.substring(1, commandPart.length()));
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a reference
	 */
	public final static boolean isReference(String commandPart) {
		return commandPart.charAt(0) == REFERENCE_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The reference contained in this command part.
	 */
	public final static String getReference(String commandPart) {
		String reference = commandPart.substring(1, commandPart.length());

		if (reference.trim().length() == 0) {
			throw new Py4JException("Reference is empty.");
		}

		return reference;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a reference
	 */
	public final static boolean isString(String commandPart) {
		return commandPart.charAt(0) == STRING_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The reference contained in this command part.
	 */
	public final static String getString(String commandPart) {
		String toReturn = "";
		if (commandPart.length() >= 2) {
			toReturn = StringUtil.unescape(commandPart.substring(1, commandPart
					.length()));
		}
		return toReturn;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is null
	 */
	public final static boolean isNull(String commandPart) {
		return commandPart.charAt(0) == NULL_TYPE;
	}

	/**
	 * <p>
	 * Method provided for consistency. Just returns null.
	 * </p>
	 * 
	 * @param commandPart
	 * @return null.
	 */
	public final static Object getNull(String commandPart) {
		return null;
	}

	public final static Object getObject(String commandPart, Gateway gateway) {
		Object obj = getObject(commandPart);
		if (isReference(commandPart)) {
			obj = gateway.getObject((String) obj);
		}
		return obj;
	}

	public final static Object getObject(String commandPart) {
		if (isEmpty(commandPart) || isEnd(commandPart)) {
			throw new Py4JException(
					"Command Part is Empty or is the End of Command Part");
		} else if (isReference(commandPart)) {
			return getReference(commandPart);
		} else if (isInteger(commandPart)) {
			return getInteger(commandPart);
		} else if (isBoolean(commandPart)) {
			return getBoolean(commandPart);
		} else if (isDouble(commandPart)) {
			return getDouble(commandPart);
		} else if (isString(commandPart)) {
			return getString(commandPart);
		} else if (isNull(commandPart)) {
			return getNull(commandPart);
		} else {
			throw new Py4JException("Command Part is unknown.");
		}
	}

	public final static String getOutputErrorCommand() {
		return ERROR_COMMAND;
	}

	public final static String getOutputVoidCommand() {
		return VOID_COMMAND;
	}

	public final static String getMemberOutputCommand(char memberType) {
		StringBuilder builder = new StringBuilder();

		builder.append(SUCCESS);
		builder.append(memberType);
		builder.append(END_OUTPUT);

		return builder.toString();
	}

	public final static String getOutputCommand(ReturnObject rObject) {
		StringBuilder builder = new StringBuilder();

		if (rObject.isError()) {
			builder.append(ERROR);
		} else {
			builder.append(SUCCESS);
			if (rObject.isNull()) {
				builder.append(NULL_TYPE);
			} else if (rObject.isVoid()) {
				builder.append(VOID);
			} else if (rObject.isList()) {
				builder.append(LIST_TYPE);
				builder.append(rObject.getName());
			} else if (rObject.isMap()) {
				builder.append(MAP_TYPE);
				builder.append(rObject.getName());
			} else if (rObject.isReference()) {
				builder.append(REFERENCE_TYPE);
				builder.append(rObject.getName());
			} else {
				Object primitiveObject = rObject.getPrimitiveObject();
				char primitiveType = getPrimitiveType(primitiveObject);
				builder.append(getPrimitiveType(primitiveObject));
				if (primitiveType == STRING_TYPE) {
					builder.append(StringUtil
							.escape(primitiveObject.toString()));
				} else {
					builder.append(primitiveObject.toString());
				}

			}
		}
		builder.append(END_OUTPUT);

		return builder.toString();
	}

	private static char getPrimitiveType(Object primitiveObject) {
		char c = INTEGER_TYPE;

		if (primitiveObject instanceof String
				|| primitiveObject instanceof Character) {
			c = STRING_TYPE;
		} else if (primitiveObject instanceof Double
				|| primitiveObject instanceof Float) {
			c = DOUBLE_TYPE;
		} else if (primitiveObject instanceof Boolean) {
			c = BOOLEAN_TYPE;
		}

		return c;
	}

	public static String getNoSuchFieldOutputCommand() {
		return NO_SUCH_FIELD;
	}
}
